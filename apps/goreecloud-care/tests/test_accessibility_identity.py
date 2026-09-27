from pathlib import Path
import unittest


class AccessibilityIdentityTests(unittest.TestCase):
    def _entrypoint(self):
        return (
            Path(__file__).resolve().parents[1]
            / "goreecloud_care"
            / "__main__.py"
        ).read_text(encoding="utf-8")

    def test_entrypoint_sets_product_program_name_before_gui_import(self):
        entrypoint = self._entrypoint()
        identity = 'GLib.set_prgname("GoreeCloud Care")'
        gui_import = "from .app import main"
        launch = "return main()"
        self.assertIn(identity, entrypoint)
        self.assertIn(gui_import, entrypoint)
        self.assertIn(launch, entrypoint)
        self.assertLess(entrypoint.index(identity), entrypoint.index(gui_import))
        self.assertLess(entrypoint.index(identity), entrypoint.index(launch))

    def test_entrypoint_sets_product_application_name_before_gui_import(self):
        entrypoint = self._entrypoint()
        identity = 'GLib.set_application_name("GoreeCloud Care")'
        gui_import = "from .app import main"
        launch = "return main()"
        self.assertIn(identity, entrypoint)
        self.assertIn(gui_import, entrypoint)
        self.assertIn(launch, entrypoint)
        self.assertLess(entrypoint.index(identity), entrypoint.index(gui_import))
        self.assertLess(entrypoint.index(identity), entrypoint.index(launch))

    def test_program_identity_precedes_application_identity(self):
        entrypoint = self._entrypoint()
        program_identity = 'GLib.set_prgname("GoreeCloud Care")'
        application_identity = 'GLib.set_application_name("GoreeCloud Care")'
        self.assertLess(
            entrypoint.index(program_identity),
            entrypoint.index(application_identity),
        )

    def test_report_modes_keep_gui_import_lazy(self):
        entrypoint = self._entrypoint()
        report_branch = "if report_requested or json_report_requested:"
        gui_import = "from .app import main"
        self.assertLess(entrypoint.index(report_branch), entrypoint.index(gui_import))


if __name__ == "__main__":
    unittest.main()
