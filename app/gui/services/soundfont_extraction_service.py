from pathlib import Path

from app.core.n64_rom import Soundfont


class SoundfontExtractionService:
    def __init__(self, soundfont: Soundfont, output_dir: Path, view_model):
        self.soundfont: Soundfont = soundfont
        self.output_dir: Path = output_dir
        self.view_model = view_model

        self.success_emitter = view_model.operation_succeeded
        self.fail_emitter = view_model.operation_failed
        self.overwrit_emitter = view_model.overwrite_requested

        self.targets = {}
        self.pending = 0
        self.completed = 0

        self.had_overwrite_prompt = False
        self.errors = []

    def prepare(self):
        base_path: Path = self.output_dir / f'{self.soundfont.index:02X}'

        self.targets = {
            'zbank': base_path.with_suffix('.zbank'),
            'bankmeta': base_path.with_suffix('.bankmeta'),
        }

        self.pending = len(self.targets)

    def start(self):
        for kind, path in self.targets.items():
            self._write(kind, path)

    def _write(self, kind: str, path: Path):
        def proceed(should_write: bool):
            try:
                if not should_write:
                    self.completed += 1
                    self._finish()
                    return

                existed = path.exists()

                if kind == 'zbank':
                    self.soundfont.write_soundfont(path)
                else:
                    self.soundfont.write_table_entry(path)

                if existed:
                    self.success_emitter.emit(
                        f'Extracted and replaced "{path.name}" in: "{self.output_dir}"'
                    )
                # else:
                #     self.success_emitter.emit(
                #         f'Extracted "{path.name}" to: {self.output_dir}'
                #     )

            except Exception as ex:
                self.errors.append(str(ex))

            finally:
                self.completed += 1
                self._finish()

        if path.exists():
            self.had_overwrite_prompt = True
            self.overwrit_emitter.emit(path, proceed)
        else:
            proceed(True)

    def _finish(self):
        if self.completed != self.pending:
            return

        if self.errors:
            self.fail_emitter.emit('/n'.join(self.errors))
            return

        if not self.had_overwrite_prompt:
            zbank = self.targets['zbank'].name
            bankmeta = self.targets['bankmeta'].name

            self.success_emitter.emit(
                f'Extracted "{zbank}" and "{bankmeta}" to: "{self.output_dir}"'
            )