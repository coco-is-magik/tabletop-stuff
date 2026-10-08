package pcgen.system;

import pcgen.core.Campaign;
import pcgen.core.GameMode;
import pcgen.core.Globals;
import pcgen.core.SystemCollections;
import pcgen.facade.core.SourceSelectionFacade;
import pcgen.facade.util.ListFacade;

/**
 * Replicates the data source behind the GUI Source Selection dialog.
 *
 * The Advanced tab lists {@code FacadeFactory.getSupportedCampaigns(mode)} and the
 * Basic tab lists {@code getDisplayedSourceSelections()}; both need
 * {@code FacadeFactory.initialize()} to have run, which only the GUI startup does.
 */
public class PcgenGuiSources {
    public static void main(String[] args) throws Exception {
        require(pcgen.system.Main.loadCharacterAndExport(args[0], args[1], args[2], args[3]),
                "Load failed");
        FacadeFactory.initialize();
        System.out.println("loaded campaigns: " + Globals.getCampaignList().size());

        boolean spheresSupported = false;
        for (GameMode mode : SystemCollections.getUnmodifiableGameModeList()) {
            ListFacade<Campaign> list = FacadeFactory.getSupportedCampaigns(mode);
            int hits = 0;
            for (int i = 0; i < list.getSize(); i++) {
                if (list.getElementAt(i).getKeyName().startsWith("Spheres PF1e")) {
                    hits++;
                }
            }
            if (hits > 0) {
                System.out.println("ADVANCED_TAB " + mode.getName() + " lists Spheres x" + hits
                        + " (of " + list.getSize() + " campaigns)");
                spheresSupported = true;
            }
        }

        boolean spheresDisplayed = false;
        ListFacade<SourceSelectionFacade> displayed = FacadeFactory.getDisplayedSourceSelections();
        for (int i = 0; i < displayed.getSize(); i++) {
            ListFacade<Campaign> campaigns = displayed.getElementAt(i).getCampaigns();
            for (int j = 0; j < campaigns.getSize(); j++) {
                if (campaigns.getElementAt(j).getKeyName().startsWith("Spheres PF1e")) {
                    spheresDisplayed = true;
                    System.out.println("BASIC_TAB lists " + campaigns.getElementAt(j).getKeyName());
                }
            }
        }
        System.out.println("basic tab entries: " + displayed.getSize());

        require(spheresSupported, "Spheres campaign is not offered by the Advanced tab");
        System.out.println("SPHERES_GUI_SOURCES_OK " + spheresDisplayed);
        System.exit(0);
    }

    private static void require(boolean condition, String message) {
        if (!condition) {
            throw new IllegalStateException(message);
        }
    }
}
