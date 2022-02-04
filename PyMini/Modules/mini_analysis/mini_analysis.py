from PyMini.Modules.base_module import BaseModule
from PyMini import app
import os
from PyMini.utils import formatting
from PyMini.Layout import batch_popup
class Module(BaseModule):
    def __init__(self):
        super().__init__(
            name='mini_analysis',
            menu_label='Mini Analysis',
            tab_label='Mini',
            filename=__file__
        )

        if app.widgets['trace_mode'].get() != 'continuous':
            try:
                self._add_disable()
            except:
                pass
        self._load_batch()

    def update_module_display(self, table=False):
        super().update_module_display()

        if self.menu_var.get():
            self.control_tab.update_event_markers(draw=True)
        else:
            for m in self.control_tab.markers:
                try:
                    self.control_tab.markers[m].remove()
                except:
                    pass
            app.trace_display.draw_ani()
        app.pb['value'] = 0
        app.pb.update()

    def _load_batch(self):
        batch_popup.insert_command_category('Mini analysis')
        batch_popup.insert_command('Find all', 'Mini analysis', lambda
            func=lambda i=False: self.control_tab.find_mini_all_thread(i): self.control_tab.call_if_enabled(func),
                                       interrupt=app.interface.al)
        batch_popup.insert_command('Find in window', 'Mini analysis',
                                       lambda func=lambda i=False: self.control_tab.find_mini_range_thread(
                                           i): self.control_tab.call_if_enabled(func),
                                       interrupt=app.interface.al)
        batch_popup.insert_command('Delete all', 'Mini analysis', lambda func=self.control_tab.delete_all: self.control_tab.call_if_enabled(func))
        batch_popup.insert_command('Delete in window', 'Mini analysis', lambda func=self.control_tab.delete_in_window: self.control_tab.call_if_enabled(func))
        batch_popup.insert_command('Report results', 'Mini analysis', lambda func=self.control_tab.report_results: self.control_tab.call_if_enabled(func))
        def save_minis():
            if self.control_tab.mini_df.shape[0]== 0:
                batch_popup.batch_log.insert('Warning: Exporting an empty data table\n')
            fname = formatting.format_save_filename(os.path.splitext(batch_popup.file_list[batch_popup.file_idx])[0]+'.mini', overwrite=False)
            self.control_tab.save_minis(fname, overwrite=False)
            batch_popup.batch_log.insert(f"Saved minis to: {fname}\n")
        batch_popup.insert_command('Save minis', 'Mini analysis', lambda func=save_minis: self.control_tab.call_if_enabled(func))
        def export_minis():
            if len(self.data_tab.table.get_children()) == 0:
                batch_popup.batch_log.insert('Warning: Exporting an empty data table\n')
            fname = formatting.format_save_filename(
                os.path.splitext(batch_popup.file_list[batch_popup.file_idx])[0] + '_minis.csv', overwrite=False)
            self.data_tab.export(fname, overwrite='False')
            batch_popup.batch_log.insert(f"Exported minis to: {fname}\n")
        batch_popup.insert_command('Export minis', 'Mini analysis', lambda func=export_minis:self.control_tab.call_if_enabled(func))


