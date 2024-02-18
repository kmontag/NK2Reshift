SYSTEM_MIDI_REMOTE_SCRIPTS_DIR := /Applications/Ableton\ Live\ 11\ Suite.app/Contents/App-Resources/MIDI\ Remote\ Scripts

.PHONY: deps
deps: __ext__/System_MIDIRemoteScripts/.make.decompile .make.pip-install

.PHONY: check
check: .make.pip-install __ext__/System_MIDIRemoteScripts/.make.decompile
	.venv/bin/pyright .

.PHONY: lint
lint: .make.pip-install
	.venv/bin/ruff format --check .
	.venv/bin/ruff check .

.PHONY: fix
fix: .make.pip-install
	.venv/bin/ruff format .
	.venv/bin/ruff check --fix .

.PHONY: clean
clean:
	rm -rf .venv/
	rm -rf __ext/System_MIDIRemoteScripts/
	rm -f .make.*

__ext__/System_MIDIRemoteScripts/.make.decompile: $(SYSTEM_MIDI_REMOTE_SCRIPTS_DIR) | .make.pip-install
	rm -rf $(@D)/
	mkdir -p $(@D)/ableton/
# decompyle3 works for most files, and the ones where it throws errors
# don't matter for our purposes.
	.venv/bin/decompyle3 -r -o $(@D)/ableton/ $(SYSTEM_MIDI_REMOTE_SCRIPTS_DIR)/ableton/
	touch $@

.venv:
	python -m venv .venv

.make.pip-install: .venv requirements.txt .python-version
	.venv/bin/pip install -r requirements.txt
	touch .make.pip-install
