from SimplyFire.Modules.base_module import BaseModule
from SimplyFire.Layout import batch_popup
from SimplyFire.utils import formatting
import os
class Module(BaseModule):
    def __init__(self):
        super().__init__(
            name='evoked_basic',
            menu_label='Evoked Analysis',
            tab_label='Evoked',
        )

        self._load_batch()


    def _load_batch(self):
        batch_popup.insert_command_category('Evoked Analysis')
        batch_popup.insert_command('Calculate min/max', 'Evoked Analysis', self.control_tab.calculate_min_max)
        batch_popup.insert_command('Report results', 'Evoked Analysis', self.data_tab.report)
        def export_results():
            if len(self.data_tab.table.get_children())== 0:
                batch_popup.batch_log.insert('Warning: Exporting an empty data table\n')
            fname = formatting.format_save_filename(os.path.splitext(batch_popup.file_list[batch_popup.file_idx])[0]+'_EvokedAnalysis.csv', overwrite=False)
            self.data_tab.export(fname, overwrite=False)
            batch_popup.batch_log.insert(f"Saved evoked analysis results to: {fname}\n")
        batch_popup.insert_command('Export results', 'Evoked Analysis', export_results)


