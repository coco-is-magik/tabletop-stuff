#!/usr/bin/env python3
"""Repeat PCGen 6.08.00RC10 preparation and offline compilation or data testing.

Usage:
    python3 pcgen_build_with_tests_fixed.py /path/to/workspace
    python3 pcgen_build_with_tests_fixed.py /path/to/workspace --datatest
    python3 pcgen_build_with_tests_fixed.py /path/to/pcgen-6.08.00RC10 --prepare-datatest
    python3 pcgen_build_with_tests_fixed.py /path/to/workspace --datatest --offline

Default: the original compile-only workflow, unchanged.
--datatest: resolve real main/test/slowtest artifacts online, prepare Linux
JavaFX 16 modules at mods/lib if missing, then run the filtered DataLoadTest
OFFLINE with JUnit Platform and JDK 16. Actual test failures remain failures.
--prepare-datatest: prepare dependencies/modules and verify offline resolution,
without source compilation or test execution.
--offline: no JDK download and no online Gradle invocation in any mode.

Uses a private JDK and the existing download-task patch. The test workflow
applies a temporary Gradle init script, not a permanent datatest build edit.
Existing complete JavaFX 16 module directories are reused; incomplete existing
directories are not replaced. Unversioned module descriptors are accepted
only when the JAR contents match the resolved JavaFX 16 artifacts. The Maven-based mods/lib directory is NOT a full
SDK, a JMOD bundle, or cross-platform runtime-image provisioning.
Python 3.9+, Linux x86_64/glibc. Initial JDK installation requires curl and tar.
No sudo, pip, or Portage changes. Gradle --offline is not a network sandbox.

References:
https://docs.oracle.com/en/java/javase/16/docs/api/java.base/java/lang/module/ModuleDescriptor.html#version()
https://raw.githubusercontent.com/PCGen/pcgen/6.08.00RC10/build.gradle
https://github.com/adoptium/temurin16-binaries/releases/tag/jdk-16.0.2%2B7
https://raw.githubusercontent.com/gradle/gradle/v7.3.0/subprojects/docs/src/docs/userguide/jvm/toolchains.adoc
https://raw.githubusercontent.com/gradle/gradle/v7.3.0/subprojects/docs/src/docs/userguide/reference/command_line_interface.adoc
https://raw.githubusercontent.com/gradle/gradle/v7.3.0/subprojects/wrapper/src/main/java/org/gradle/wrapper/PathAssembler.java
https://raw.githubusercontent.com/gradle/gradle/v7.3.0/subprojects/wrapper/src/main/java/org/gradle/wrapper/Install.java
https://raw.githubusercontent.com/gradle/gradle/v7.3.0/subprojects/core-api/src/main/java/org/gradle/api/artifacts/Configuration.java
https://raw.githubusercontent.com/PCGen/pcgen/6.08.00RC10/code/src/test/pcgen/persistence/lst/DataLoadTest.java
https://github.com/openjdk/jfx/blob/jfx16/modules/javafx.graphics/src/main/java/com/sun/glass/utils/NativeLibLoader.java
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import difflib
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shlex
import shutil
import stat
import subprocess
import sys
import tempfile
import uuid
import zipfile
from urllib.parse import unquote, urlsplit

ARCHIVE = "OpenJDK16U-jdk_x64_linux_hotspot_16.0.2_7.tar.gz"
RELEASE_URL = "https://github.com/adoptium/temurin16-binaries/releases/download/jdk-16.0.2%2B7"
VENDORED = Path("vendor/upstream/pcgen-6.08.00RC10")
MARKERS = (
    "task downloadJRE {",
    "task downloadJavaFXModules(dependsOn: downloadJRE) {",
    "compileJava.dependsOn(downloadJavaFXModules)",
)


class BuildError(Exception):
    """An expected failure that can be reported without a Python traceback."""


def log(message: str) -> None:
    print(f"[pcgen] {message}", flush=True)


def absolute(path: str | Path) -> Path:
    # Do not resolve the final symlink here: a broken JDK symlink must be refused.
    return Path(os.path.abspath(Path(path).expanduser()))


def run(command: list[str], *, cwd: Path | None = None,
        env: dict[str, str] | None = None) -> None:
    log("$ " + shlex.join(command))
    subprocess.run(command, cwd=cwd, env=env, check=True)


@contextmanager
def locked(path: Path):
    import fcntl
    # Keep the lock file after unlocking; deleting it would permit an inode race.
    with path.open("a") as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise BuildError(f"Another script instance holds this lock: {path}") from exc
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def locate_project(argument: Path) -> Path:
    root = absolute(argument).resolve(strict=True)
    for candidate in (root, root / VENDORED):
        if (candidate / "gradlew").is_file() and (candidate / "build.gradle").is_file():
            return candidate.resolve(strict=True)
    raise BuildError(
        f"No PCGen checkout found at {root} or {root / VENDORED}. "
        "Pass the directory containing PCGen's gradlew and build.gradle."
    )


def wrapper_properties(project: Path) -> dict[str, str]:
    props = {}
    path = project / "gradle/wrapper/gradle-wrapper.properties"
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith(("#", "!")) and "=" in line:
            key, value = line.split("=", 1)
            props[key.strip()] = value.strip().replace(r"\:", ":")
    if not re.fullmatch(
        r"https://services\.gradle\.org/distributions/gradle-7\.3-(all|bin)\.zip",
        props.get("distributionUrl", ""),
    ):
        raise BuildError("Expected PCGen's Gradle 7.3 wrapper URL; no wrapper change was made.")
    for key in ("distributionBase", "zipStoreBase"):
        if props.get(key, "GRADLE_USER_HOME") != "GRADLE_USER_HOME":
            raise BuildError(f"Unsupported wrapper setting: {key}. Expected GRADLE_USER_HOME.")
    for key in ("distributionPath", "zipStorePath"):
        if props.get(key, "wrapper/dists") != "wrapper/dists":
            raise BuildError(f"Unsupported wrapper setting: {key}. Expected wrapper/dists.")
    if not (project / "gradle/wrapper/gradle-wrapper.jar").is_file():
        raise BuildError("gradle/wrapper/gradle-wrapper.jar is missing from this checkout.")
    return props


def require_offline_wrapper(cache: Path, props: dict[str, str]) -> None:
    # The wrapper bootstraps before Gradle can process --offline. Check its
    # exact URL-keyed cache first, rather than letting it attempt a download.
    url = props["distributionUrl"]
    number = int.from_bytes(hashlib.md5(url.encode("utf-8")).digest(), "big")
    digits = "0123456789abcdefghijklmnopqrstuvwxyz"
    encoded = ""
    while number:
        number, remainder = divmod(number, 36)
        encoded = digits[remainder] + encoded
    name = url.rsplit("/", 1)[1]
    directory = cache / "wrapper/dists" / name[:-4] / (encoded or "0")
    launcher = directory / "gradle-7.3/lib/gradle-launcher-7.3.jar"
    if not directory.is_dir():
        raise BuildError(f"Offline Gradle wrapper cache is missing: {directory}")
    directories = [item for item in directory.iterdir() if item.is_dir()]
    if (not (directory / (name + ".ok")).is_file() or not launcher.is_file()
            or len(directories) != 1):
        raise BuildError(f"Offline Gradle wrapper cache is incomplete: {directory}")


def transform(text: str) -> str:
    """Apply the same minimal doLast wrappers, without wrapping a second time."""
    if not re.search(r"JavaLanguageVersion\.of\(\s*16\s*\)", text):
        raise BuildError("This build does not declare the expected Java 16 toolchain.")
    if not re.search(r"javafx\s*\{\s*version\s*=\s*(['\"])16\1", text):
        raise BuildError("This build does not declare the expected JavaFX 16 version.")
    newline = "\r\n" if "\r\n" in text else "\n"
    lines = text.splitlines(keepends=True)
    positions = []
    for marker in MARKERS:
        found = [i for i, line in enumerate(lines) if line.strip() == marker]
        if len(found) != 1:
            raise BuildError(f"Expected exactly one {marker!r}; found {len(found)}. No patch applied.")
        positions.append(found[0])
    if positions != sorted(positions):
        raise BuildError("The download tasks are not in the expected order. No patch applied.")
    for index in (1, 0):
        start, boundary = positions[index], positions[index + 1]
        closing = boundary - 1
        while closing > start and not lines[closing].strip():
            closing -= 1
        if lines[closing].strip() != "}":
            raise BuildError(f"Unexpected ending for {MARKERS[index]!r}. No patch applied.")
        body = [line.strip() for line in lines[start + 1:closing]
                if line.strip() and not line.lstrip().startswith("//")]
        expected = "def major = 16" if index == 0 else 'def major = "16"'
        if body and body[0] == "doLast {":
            if len(body) < 3 or body[1] != expected or body[-1] != "}":
                raise BuildError("An existing doLast wrapper has an unexpected body. No patch applied.")
            continue
        if not body or body[0] != expected:
            raise BuildError(f"Unexpected body for {MARKERS[index]!r}. No patch applied.")
        if any(re.search(r"\bdo(?:First|Last)\s*\{", line) for line in body):
            raise BuildError("An unexpected task action already exists. No patch applied.")
        lines.insert(closing, "    }" + newline)
        lines.insert(start + 1, "    doLast {" + newline)
    return "".join(lines)


def apply_patch(path: Path, original: bytes, modified: bytes) -> None:
    if path.read_bytes() != original:
        raise BuildError("build.gradle changed during setup. No patch applied.")
    if original == modified:
        log("Download tasks are already deferred; build.gradle is unchanged.")
        return
    mode = stat.S_IMODE(path.stat().st_mode)
    backup = path.with_name(path.name + ".before-deferred-downloads")
    if backup.exists() or backup.is_symlink():
        if backup.is_symlink() or not backup.is_file() or backup.read_bytes() != original:
            suffix = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            backup = backup.with_name(backup.name + "." + suffix + "." + uuid.uuid4().hex[:8])
    if not backup.exists():
        with backup.open("xb") as stream:
            stream.write(original)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(backup, mode)
    sys.stdout.writelines(difflib.unified_diff(
        original.decode("utf-8").splitlines(keepends=True),
        modified.decode("utf-8").splitlines(keepends=True),
        fromfile=str(path), tofile=str(path) + " (deferred downloads)",
    ))
    fd, name = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(modified)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(name, mode)
        if path.read_bytes() != original:
            raise BuildError("build.gradle changed while preparing the patch. It was not overwritten.")
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)
    log(f"Patch applied. Backup: {backup}")


def java_details(executable: Path) -> tuple[int, Path]:
    if not executable.is_file() or not os.access(executable, os.X_OK):
        raise BuildError(f"Java executable is missing or not executable: {executable}")
    result = subprocess.run([str(executable), "-XshowSettings:properties", "-version"],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=True)
    version = re.search(r"(?m)^\s*java\.specification\.version\s*=\s*(\S+)\s*$", result.stdout)
    home = re.search(r"(?m)^\s*java\.home\s*=\s*(.+?)\s*$", result.stdout)
    if not version or not home:
        raise BuildError(f"Could not identify Java version/home:\n{result.stdout}")
    value = version.group(1)
    major = int(value.split(".")[1] if value.startswith("1.") else value.split(".")[0])
    return major, Path(home.group(1)).resolve(strict=True)


def validate_jdk16(path: Path) -> None:
    major, _ = java_details(path / "bin/java")
    compiler = path / "bin/javac"
    if major != 16 or not compiler.is_file() or not os.access(compiler, os.X_OK):
        raise BuildError(f"Expected a working full JDK 16 at {path}; existing files were not replaced.")
    output = subprocess.check_output([str(compiler), "-version"], stderr=subprocess.STDOUT, text=True)
    if not re.search(r"(?m)^javac 16(?:[.\s+\-]|$)", output):
        raise BuildError(f"Expected javac 16 at {path}, got: {output.strip()}")
    if not (path / "jmods/java.base.jmod").is_file():
        raise BuildError(f"This does not appear to be a full modular JDK: {path}")
    log(f"JDK 16: {path} ({output.strip()})")


def verify_archive(archive: Path, checksum: Path) -> None:
    match = re.fullmatch(r"([0-9a-fA-F]{64})\s+\*?" + re.escape(ARCHIVE),
                         checksum.read_text(encoding="ascii").strip())
    if not match:
        raise BuildError("The downloaded JDK checksum file has an unexpected format or filename.")
    digest = hashlib.sha256()
    with archive.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    if digest.hexdigest() != match.group(1).lower():
        raise BuildError("JDK archive SHA-256 verification failed. Nothing was installed.")
    log("JDK archive SHA-256 verified.")


def ensure_jdk16(path: Path, offline: bool) -> None:
    if path.exists() or path.is_symlink():
        validate_jdk16(path)
        return
    if offline:
        raise BuildError(f"JDK 16 is missing in offline mode: {path}")
    for command in ("curl", "tar"):
        if shutil.which(command) is None:
            raise BuildError(f"First-time JDK installation requires {command}.")
    path.parent.mkdir(parents=True, exist_ok=True)
    with locked(path.parent / ("." + path.name + ".pcgen-install.lock")):
        if path.exists() or path.is_symlink():
            validate_jdk16(path)
            return
        with tempfile.TemporaryDirectory(prefix=".pcgen-jdk16-", dir=path.parent) as directory:
            work = Path(directory)
            log("Installing private Temurin 16.0.2+7.")
            for name in (ARCHIVE, ARCHIVE + ".sha256.txt"):
                run(["curl", "--fail", "--location", "--retry", "3", "--connect-timeout", "30",
                     "--proto", "=https", "--proto-redir", "=https",
                     "--output", str(work / name), RELEASE_URL + "/" + name])
            verify_archive(work / ARCHIVE, work / (ARCHIVE + ".sha256.txt"))
            unpacked = work / "unpacked"
            unpacked.mkdir()
            run(["tar", "--extract", "--gzip", "--file", str(work / ARCHIVE),
                 "--directory", str(unpacked), "--strip-components=1", "--no-same-owner"])
            validate_jdk16(unpacked)
            if path.exists() or path.is_symlink():
                raise BuildError(f"The JDK destination appeared during installation: {path}")
            unpacked.rename(path)
        log(f"Installed JDK 16 at: {path}")


def select_gradle_java(explicit: Path | None, jdk16: Path) -> Path:
    if explicit is not None:
        major, home = java_details(absolute(explicit) / "bin/java")
        if major not in (16, 17):
            raise BuildError("--gradle-java-home must supply Java 16 or 17 for this script.")
    else:
        candidate = (Path(os.environ["JAVA_HOME"]) / "bin/java"
                     if os.environ.get("JAVA_HOME") else Path(shutil.which("java") or "/missing/java"))
        try:
            major, home = java_details(candidate)
        except (BuildError, OSError, ValueError, subprocess.CalledProcessError):
            major, home = 0, jdk16
        if major not in (16, 17):
            log("Current Java is not a usable Java 16/17; using the private JDK 16 for Gradle.")
            major, home = java_details(jdk16 / "bin/java")
    log(f"Gradle JVM: Java {major} at {home}; system Java selection is unchanged.")
    return home


# The initialization script is applied only to these invocations. It does not
# rewrite the upstream dependency declarations or the datatest task in build.gradle.
DATATEST_INIT = r'''
import groovy.json.JsonOutput
import org.gradle.api.GradleException
import org.gradle.api.tasks.testing.Test
import org.gradle.jvm.toolchain.JavaLanguageVersion
import org.gradle.jvm.toolchain.JavaToolchainService

gradle.projectsEvaluated {
    def p = gradle.rootProject
    def fx = p.configurations.create('pcgenDataTestJavafx16')
    fx.canBeConsumed = false
    fx.canBeResolved = true
    // All seven modules are explicit, so do not pull unclassified placeholder JARs.
    fx.transitive = false
    ['base', 'graphics', 'controls', 'fxml', 'media', 'swing', 'web'].each { m ->
        p.dependencies.add(fx.name, "org.openjfx:javafx-${m}:16:linux")
    }

    p.tasks.register('pcgenResolveDataTestDependencies') {
        group = 'verification'
        description = 'Resolve actual main/test/slowtest dependency files without compiling or testing.'
        doLast {
            ['compileClasspath', 'runtimeClasspath',
             'testCompileClasspath', 'testRuntimeClasspath',
             'slowtestCompileClasspath', 'slowtestRuntimeClasspath'].each { name ->
                def configuration = p.configurations.getByName(name)
                if (!configuration.canBeResolved) {
                    throw new GradleException("Not a resolvable configuration: ${name}")
                }
                def files = configuration.resolve()
                p.logger.lifecycle("[pcgen] Resolved ${name}: ${files.size()} files")
            }
            def files = fx.resolve().sort { it.name }
            def destination = p.findProperty('pcgenResolvedJavafx')
            if (!destination) {
                throw new GradleException('Missing -PpcgenResolvedJavafx output path')
            }
            p.file(destination.toString()).setText(
                JsonOutput.toJson(files.collect { it.absolutePath }), 'UTF-8')
            p.logger.lifecycle("[pcgen] Resolved Linux JavaFX 16: ${files.size()} files")
        }
    }

    p.tasks.named('datatest', Test).configure { t ->
        t.useJUnitPlatform()
        t.ignoreFailures = false
        t.filter.setFailOnNoMatchingTests(true)
        t.javaLauncher.set(p.extensions.getByType(JavaToolchainService).launcherFor {
            languageVersion = JavaLanguageVersion.of(16)
        })
        t.afterSuite { descriptor, result ->
            if (descriptor.parent == null) {
                def destination = p.findProperty('pcgenDataTestSummary')
                if (destination) {
                    p.file(destination.toString()).setText(JsonOutput.toJson([
                        tests: result.testCount,
                        passed: result.successfulTestCount,
                        failed: result.failedTestCount,
                        skipped: result.skippedTestCount
                    ]), 'UTF-8')
                }
                p.logger.lifecycle("[pcgen] datatest: ${result.testCount} tests, " +
                    "${result.failedTestCount} failed, ${result.skippedTestCount} skipped")
            }
        }
    }
}
'''

FX_MODULES = ('base', 'graphics', 'controls', 'fxml', 'media', 'swing', 'web')


def read_fx_artifacts(path: Path) -> list[Path]:
    """Read only the seven versioned, Linux-classified artifacts requested above."""
    value = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise BuildError('Gradle returned an invalid JavaFX artifact manifest.')
    paths = [Path(item) for item in value]
    expected = {f'javafx-{module}-16-linux.jar' for module in FX_MODULES}
    if len(paths) != len(expected) or {item.name for item in paths} != expected:
        raise BuildError('Expected exactly the seven Linux JavaFX 16 module JARs.')
    for item in paths:
        if not item.is_absolute() or not item.is_file():
            raise BuildError(f'Resolved JavaFX artifact is missing: {item}')
        try:
            with zipfile.ZipFile(item) as archive:
                names = archive.namelist()
                if 'module-info.class' not in names:
                    raise BuildError(f'JavaFX artifact has no module descriptor: {item}')
                if item.name in {f'javafx-{m}-16-linux.jar' for m in ('graphics', 'media', 'web')}:
                    if not any(name.endswith('.so') for name in names):
                        raise BuildError(f'JavaFX artifact has no Linux native libraries: {item}')
        except zipfile.BadZipFile as exc:
            raise BuildError(f'Invalid JavaFX JAR: {item}') from exc
    return sorted(paths, key=lambda item: item.name)


def sha256_file(path: Path) -> str:
    """Hash a file without loading the full JAR into memory."""
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def validate_test_modules(directory: Path, jdk16: Path,
                          artifacts: list[Path] | None = None) -> None:
    """Read module names; a JPMS module version is optional, not the Maven version.

    Maven JavaFX 16 JARs can appear as "javafx.base file:///...", with no
    "@16". For an unversioned descriptor, require the exact bytes of the
    corresponding Gradle-resolved version-16 Linux artifact. Existing SDK
    modules with an explicit version 16 remain supported.
    """
    if not directory.is_dir():
        raise BuildError(f'JavaFX module directory is missing: {directory}')
    result = subprocess.run(
        [str(jdk16 / 'bin/java'), '--module-path', str(directory), '--list-modules'],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=False,
    )
    if result.returncode != 0:
        raise BuildError(
            f'Java could not read the module directory {directory}. '
            'Existing files were not overwritten.\n' + result.stdout
        )
    modules: dict[str, tuple[str | None, str | None]] = {}
    problems = []
    for line in result.stdout.splitlines():
        fields = line.split()
        if not fields:
            continue
        match = re.fullmatch(r'(javafx\.[A-Za-z0-9_.]+)(?:@([^\s]+))?', fields[0])
        if not match:
            continue
        name, version = match.groups()
        if name in modules:
            problems.append(f'{name}: duplicate module entry')
        if 'automatic' in fields[1:]:
            problems.append(f'{name}: expected an explicit module descriptor')
        location = next((field for field in fields[1:] if field.startswith('file:')), None)
        modules[name] = (version, location)

    resolved = {artifact.name: artifact for artifact in (artifacts or [])}
    for suffix in FX_MODULES:
        name = 'javafx.' + suffix
        if name not in modules:
            problems.append(f'{name}: missing')
            continue
        version, location = modules[name]
        if version is not None:
            if not re.match(r'^16(?:[.+\-]|$)', version):
                problems.append(f'{name}: expected version 16, found {version}')
            continue

        # Do not infer the version from a filename or silently accept unknown
        # unversioned modules. Match against the already resolved pinned JAR.
        reference = resolved.get(f'javafx-{suffix}-16-linux.jar')
        if reference is None or not reference.is_file():
            problems.append(f'{name}: no resolved JavaFX 16 artifact for content verification')
            continue
        uri = urlsplit(location or '')
        if (uri.scheme != 'file' or uri.netloc not in ('', 'localhost')
                or uri.query or uri.fragment):
            problems.append(f'{name}: no usable local module-file location')
            continue
        module_file = Path(unquote(uri.path))
        if not module_file.is_absolute() or not module_file.is_file():
            problems.append(f'{name}: module file is missing: {module_file}')
            continue
        if not module_file.resolve().is_relative_to(directory.resolve()):
            problems.append(f'{name}: module file is outside the requested directory')
            continue
        if sha256_file(module_file) != sha256_file(reference):
            problems.append(f'{name}: contents differ from the resolved JavaFX 16 artifact')

    if problems:
        raise BuildError(
            f'JavaFX module validation failed for {directory}. '
            'Existing files were not overwritten.\n'
            + '\n'.join(problems) + '\nJava output:\n' + result.stdout
        )


def ensure_test_modules(project: Path, jdk16: Path, artifacts: list[Path]) -> None:
    """Supply upstream's mods/lib path from real Maven module JARs, not dummy files."""
    target = project / 'mods/lib'
    if target.exists() or target.is_symlink():
        validate_test_modules(target, jdk16, artifacts)
        log(f'Reusing JavaFX 16 modules: {target}')
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.pcgen-javafx16-', dir=target.parent) as tmp:
        stage = Path(tmp) / 'lib'
        stage.mkdir()
        hashes = {}
        for artifact in artifacts:
            copied = stage / artifact.name
            shutil.copyfile(artifact, copied)
            digest = hashlib.sha256()
            with copied.open('rb') as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                    digest.update(chunk)
            hashes[artifact.name] = digest.hexdigest()
        validate_test_modules(stage, jdk16, artifacts)
        (stage / 'pcgen-javafx16-maven.json').write_text(
            json.dumps({'origin': 'Gradle-resolved org.openjfx version 16, linux classifier',
                        'sha256': hashes}, indent=2) + '\n', encoding='utf-8')
        if target.exists() or target.is_symlink():
            raise BuildError(f'The JavaFX destination appeared during setup: {target}')
        stage.rename(target)
    log(f'Created {target} from seven JavaFX 16 Linux Maven artifacts.')


def verify_datatest_summary(path: Path) -> dict[str, int]:
    if not path.is_file():
        raise BuildError('Gradle did not report completed datatest execution. No test success is claimed.')
    result = json.loads(path.read_text(encoding='utf-8'))
    keys = ('tests', 'passed', 'failed', 'skipped')
    if not isinstance(result, dict) or any(
        type(result.get(key)) is not int or result[key] < 0 for key in keys
    ):
        raise BuildError('Invalid datatest execution summary.')
    if result['tests'] != result['passed'] + result['failed'] + result['skipped']:
        raise BuildError('Inconsistent datatest execution summary.')
    if result['failed'] or result['passed'] == 0:
        raise BuildError(f'No successful data-test verification: {result}')
    return result


def run_datatest_workflow(common: list[str], project: Path, jdk16: Path,
                          env: dict[str, str], offline: bool, prepare_only: bool) -> None:
    exclusions = ['-x', 'downloadJRE', '-x', 'downloadJavaFXModules', '--stacktrace']
    with tempfile.TemporaryDirectory(prefix='pcgen-datatest-') as tmp:
        directory = Path(tmp)
        init = directory / 'datatest.init.gradle'
        artifacts = directory / 'javafx.json'
        summary = directory / 'datatest-summary.json'
        init.write_text(DATATEST_INIT, encoding='utf-8')
        base = common + ['--init-script', str(init),
                         '-PpcgenResolvedJavafx=' + str(artifacts),
                         '-PpcgenDataTestSummary=' + str(summary)]
        resolve = ['pcgenResolveDataTestDependencies'] + exclusions
        log('Resolving actual main, test, slowtest, and JavaFX files' +
            (' from the offline cache.' if offline else ' with downloads allowed.'))
        run(base + (['--offline'] if offline else []) + resolve, cwd=project, env=env)
        ensure_test_modules(project, jdk16, read_fx_artifacts(artifacts))
        if prepare_only:
            if not offline:
                log('Verifying that the same dependency files resolve offline.')
                run(base + ['--offline'] + resolve, cwd=project, env=env)
                read_fx_artifacts(artifacts)
            log('SUCCESS: data-test dependency preparation verified offline. Tests were not run.')
            return
        log('Running DataLoadTest offline, with JUnit Platform and JDK 16.')
        try:
            run(base + ['--offline', '--no-build-cache', '--rerun-tasks',
                        'datatest', '--tests', 'pcgen.persistence.lst.DataLoadTest'] + exclusions,
                cwd=project, env=env)
            result = verify_datatest_summary(summary)
        finally:
            log(f'Test report location: {project / "build/reports/tests/datatest/index.html"}')
        log(f'SUCCESS: offline DataLoadTest completed; {result["passed"]} passed, '
            f'{result["skipped"]} skipped. Other test suites and packaging were not verified.')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("project", type=Path, help="PCGen checkout or enclosing workspace")
    parser.add_argument("--offline", action="store_true", help="skip JDK downloads and all online Gradle invocations")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--datatest", action="store_true",
                      help="prepare test dependencies, then force an offline DataLoadTest run")
    mode.add_argument("--prepare-datatest", action="store_true",
                      help="prepare test dependencies/modules and verify offline resolution, without tests")
    parser.add_argument("--jdk16", type=Path, default=Path.home() / ".local/lib/jvm/temurin-16.0.2+7",
                        help="JDK 16 installation directory (installed here if absent and online)")
    parser.add_argument("--gradle-user-home", type=Path,
                        default=Path(os.environ.get("GRADLE_USER_HOME") or Path.home() / ".gradle"),
                        help="Gradle cache directory (default: GRADLE_USER_HOME or ~/.gradle)")
    parser.add_argument("--gradle-java-home", type=Path,
                        help="explicit Java 16/17 home for running Gradle, not for compilation")
    args = parser.parse_args()
    if sys.version_info < (3, 9):
        raise BuildError("Python 3.9 or newer is required.")
    if platform.system() != "Linux" or platform.machine() != "x86_64":
        raise BuildError("This script targets the verified Linux x86_64 build workflow.")
    try:
        glibc = os.confstr("CS_GNU_LIBC_VERSION")
    except (OSError, ValueError):
        glibc = None
    if not glibc:
        raise BuildError("This script requires glibc, not a musl-only host.")
    project = locate_project(args.project)
    props = wrapper_properties(project)
    build_file = (project / "build.gradle").resolve(strict=True)
    jdk16 = absolute(args.jdk16)
    cache = absolute(args.gradle_user_home).resolve()
    if "," in str(jdk16) or "\n" in str(jdk16):
        raise BuildError("The JDK path cannot contain commas or newlines in Gradle's toolchain-path property.")
    log(f"PCGen checkout: {project}")
    log(f"Build file: {build_file}")
    log(f"Gradle user home: {cache}")
    with locked(project / ".pcgen-compile.lock"):
        original = build_file.read_bytes()
        modified = transform(original.decode("utf-8")).encode("utf-8")
        if args.offline:
            require_offline_wrapper(cache, props)
        ensure_jdk16(jdk16, args.offline)
        java_home = select_gradle_java(args.gradle_java_home, jdk16)
        env = os.environ.copy()
        env["JAVA_HOME"] = str(java_home)
        env["PATH"] = str(java_home / "bin") + os.pathsep + env.get("PATH", "")
        env["GRADLE_USER_HOME"] = str(cache)
        cache.mkdir(parents=True, exist_ok=True)
        apply_patch(build_file, original, modified)
        # Invoke through sh so a missing executable bit on gradlew need not change tracked files.
        common = ["sh", str(project / "gradlew"), "-p", str(project),
                  "--gradle-user-home", str(cache), "--no-daemon", "--console=plain",
                  "-Dorg.gradle.java.home=" + str(java_home),
                  "-Porg.gradle.java.installations.paths=" + str(jdk16),
                  "-Porg.gradle.java.installations.auto-download=false"]
        if args.datatest or args.prepare_datatest:
            run_datatest_workflow(common, project, jdk16, env, args.offline, args.prepare_datatest)
            return 0
        task = ["compileJava", "-x", "downloadJRE", "-x", "downloadJavaFXModules", "--stacktrace"]
        if not args.offline:
            log("Compiling with dependency downloads allowed.")
            run(common + task, cwd=project, env=env)
        log("Forcing offline compilation without cached task outputs.")
        run(common + ["--offline", "--no-build-cache", "--rerun-tasks"] + task,
            cwd=project, env=env)
        log("SUCCESS: offline compileJava completed. Tests, startup, and packaging were not run.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except subprocess.CalledProcessError as exc:
        print(f"[pcgen] FAILED: command exited with status {exc.returncode}.", file=sys.stderr)
        if exc.output:
            print(exc.output, file=sys.stderr)
        sys.exit(exc.returncode if 0 < exc.returncode < 256 else 1)
    except (BuildError, OSError, UnicodeError, ValueError) as exc:
        print(f"[pcgen] ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[pcgen] Interrupted.", file=sys.stderr)
        sys.exit(130)
