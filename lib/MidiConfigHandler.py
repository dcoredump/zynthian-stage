# -*- coding: utf-8 -*-
#********************************************************************
# ZYNTHIAN PROJECT: Zynthian Web Configurator
#
# MIDI Configuration Handler
#
# Copyright (C) 2017 Markus Heidt <markus@heidt-tech.com>
#
#********************************************************************
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of
# the License, or any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# For a full copy of the GNU General Public License see the LICENSE.txt file.
#
#********************************************************************

import os
import sys
import tornado.web
import logging
from collections import OrderedDict
from subprocess import check_output
from lib.ZynthianConfigHandler import ZynthianConfigHandler

sys.path.append(os.environ.get('ZYNTHIAN_UI_DIR'))
from zyngine.zynthian_midi_filter import MidiFilterScript

#------------------------------------------------------------------------------
# System Menu
#------------------------------------------------------------------------------

class MidiConfigHandler(ZynthianConfigHandler):

	midi_program_change_presets=OrderedDict([
		['Custom', {
			'ZYNTHIAN_MASTER_MIDI_PROGRAM_CHANGE_UP': '',
			'ZYNTHIAN_MASTER_MIDI_PROGRAM_CHANGE_DOWN': '',
			'ZYNTHIAN_MASTER_MIDI_BANK_CHANGE_UP': '',
			'ZYNTHIAN_MASTER_MIDI_BANK_CHANGE_DOWN': ''
		}],
		['Roland', {
			'ZYNTHIAN_MASTER_MIDI_PROGRAM_CHANGE_UP': 'C#7F',
			'ZYNTHIAN_MASTER_MIDI_PROGRAM_CHANGE_DOWN': 'C#00',
			'ZYNTHIAN_MASTER_MIDI_BANK_CHANGE_UP': 'B#007F',
			'ZYNTHIAN_MASTER_MIDI_BANK_CHANGE_DOWN': 'B#0000'
		}]
	])

	program_change_mode_labels=OrderedDict([
		['32', 'LSB'],
		['0', 'MSB']
	])

	midi_cc_labels=OrderedDict([
		['0', '0 - Bank Select (MSB)'],
		['1', '1 - Modulation Wheel (MSB)'],
		['2', '2 - Breath controller (MSB)'],
		['4', '4 - Foot Pedal (MSB)'],
		['5', '5 - Portamento Time (MSB)'],
		['6', '6 - Data Entry (MSB)'],
		['7', '7 - Volume (MSB)'],
		['8', '8 - Balance (MSB)'],
		['10', '10 - Pan Position (MSB)'],
		['11', '11 - Expression (MSB)'],
		['12', '12 - Effect Controller 1 (MSB)'],
		['13', '13 - Effect Controller 2 (MSB)'],

		['32', '32 - Bank Select (LSB)'],
		['33', '33 - Modulation Wheel (LSB)'],
		['34', '34 - Breath controller (LSB)'],
		['36', '36 - Foot Pedal (LSB)'],
		['37', '37 - Portamento Time (LSB)'],
		['38', '38 - Data Entry (LSB)'],
		['39', '39 - Volume (LSB)'],
		['40', '40 - Balance (LSB)'],
		['42', '42 - Pan Position (LSB)'],
		['43', '43 - Expression (LSB)'],
		['44', '44 - Effect Controller 1 (LSB)'],
		['45', '45 - Effect Controller 2 (LSB)'],

		['64', '64 - Sustain Pedal On/Off'],
		['65', '65 - Portamento On/Off'],
		['66', '66 - Sostenuto On/Off'],
		['67', '67 - Soft Pedal On/Off'],
		['68', '68 - Legato On/Off'],

		['71', '71 - VCF Resonance'],
		['72', '72 - VCA Release'],
		['73', '73 - Attack'],
		['74', '74 - VCF Cutoff Freq'],

		['84', '84 - Portamento Amount'],

		['96', '96 - Data Increment'],
		['97', '97 - Data Decrement'],
		['98', '98 - NRPN number (LSB)'],
		['99', '99 - NRPN number (MSB)'],
		['100', '100 - RPN number (LSB)'],
		['101', '101 - RPN number (MSB)'],

		['120', '120 - All Sound Off'],
		['121', '121 - Reset All Controllers'],
		['122', '122 - Local On/Off Switch'],
		['123', '123 - All Notes Off'],
		['124', '124 - Omni Mode Off'],
		['125', '125 - Omni Mode On'],
		['126', '126 - Mono Mode'],
		['127', '127 - Poly Mode']
	])

	midi_event_options=OrderedDict([
		['PG', 'Program change'],
		['KP', 'Polyphonic Key Pressure (Aftertouch)'],
		['CP', 'Channel Pressure (Aftertouch)'],
		['PB', 'Pitch Bending'],
		['CC', 'Continuous Controller Change']
	])

	@tornado.web.authenticated
	def get(self, errors=None):
		add_panel_config=OrderedDict([
			['FILTER_ADD_MIDI_EVENT', {
				'options': list(self.midi_event_options.keys()),
				'option_labels': self.midi_event_options
			}],
			['FILTER_ADD_MAPPED_MIDI_EVENT', {
				'options': list(self.midi_event_options.keys()),
				'option_labels': self.midi_event_options
			}],
			['FILTER_ADD_CC_VALUE', {
				'option_labels': self.midi_cc_labels
			}],
			['FILTER_ADD_MAPPED_CC_VALUE', {
				'option_labels': self.midi_cc_labels
			}]
		])

		config=OrderedDict([
			['ZYNTHIAN_PRESET_PRELOAD_NOTEON', {
				'type': 'boolean',
				'title': 'Preset preload on Note-On',
				'value': os.getenv('ZYNTHIAN_PRESET_PRELOAD_NOTEON',"0")
			}],
			['ZYNTHIAN_MIDI_FINE_TUNING', {
				'type': 'select',
				'title': 'MIDI fine tuning (Hz)',
				'value':  os.getenv('ZYNTHIAN_MIDI_FINE_TUNING','440'),
				'options': map(lambda x: str(x).zfill(2), list(range(392, 493)))
			}],
			['ZYNTHIAN_MASTER_MIDI_CHANNEL', {
				'type': 'select',
				'title': 'Master MIDI channel',
				'value': os.getenv('MIDI_MASTER_CHANNEL','16'),
				'options': map(lambda x: str(x).zfill(2), list(range(1, 17)))
			}],
			['ZYNTHIAN_MASTER_MIDI_BANK_CHANGE_CCNUM', {
				'type': 'select',
				'title': 'Master Bank change mode',
				'value': os.getenv('ZYNTHIAN_MASTER_MIDI_BANK_CHANGE_CCNUM',''),
				'options': list(self.program_change_mode_labels.keys()),
				'option_labels': self.program_change_mode_labels,
				'advanced': True
			}],
			['ZYNTHIAN_MASTER_MIDI_CHANGE_TYPE', {
				'type': 'select',
				'title': 'Master change type',
				'value': os.getenv('ZYNTHIAN_MASTER_MIDI_CHANGE_TYPE',''),
				'options': list(self.midi_program_change_presets.keys()),
				'presets': self.midi_program_change_presets
			}],
			['ZYNTHIAN_MASTER_MIDI_PROGRAM_CHANGE_UP', {
				'type': 'text',
				'title': 'Master Program change-up',
				'value': os.getenv('ZYNTHIAN_MASTER_MIDI_PROGRAM_CHANGE_UP',''),
				'advanced': True
			}],
			['ZYNTHIAN_MASTER_MIDI_PROGRAM_CHANGE_DOWN', {
				'type': 'text',
				'title': 'Master Program change-down',
				'value': os.getenv('ZYNTHIAN_MASTER_MIDI_PROGRAM_CHANGE_DOWN',''),
				'advanced': True
			}],
			['ZYNTHIAN_MASTER_MIDI_BANK_CHANGE_UP', {
				'type': 'text',
				'title': 'Master Bank change-up',
				'value': os.getenv('ZYNTHIAN_MASTER_MIDI_BANK_CHANGE_UP',''),
				'advanced': True
			}],
			['ZYNTHIAN_MASTER_MIDI_BANK_CHANGE_DOWN', {
				'type': 'text',
				'title': 'Master Bank change-down',
				'value': os.getenv('ZYNTHIAN_MASTER_MIDI_BANK_CHANGE_DOWN',''),
				'advanced': True
			}],
			['ZYNTHIAN_MIDI_FILTER_RULES', {
				'type': 'textarea',
				'title': 'Midi filter rules',
				'value': os.getenv('ZYNTHIAN_MIDI_FILTER_RULES',""),
				'cols': 50,
				'rows': 5,
				'addButton': 'midi_filter_rule_add',
				'addPanel': 'midi_filter_rule.html',
				'addPanelConfig': add_panel_config,
				'advanced': True
			}]
		])
		if self.genjson:
			self.write(config)
		else:
			self.render("config.html", body="config_block.html", config=config, title="MIDI", errors=errors)

	def post(self):
		self.request.arguments['ZYNTHIAN_PRESET_PRELOAD_NOTEON'] = self.request.arguments.get('ZYNTHIAN_PRESET_PRELOAD_NOTEON','0')
		escaped_request_arguments = tornado.escape.recursive_unicode(self.request.arguments)


		filterError = self.validate_filter_rules(escaped_request_arguments);

		if not filterError:
			# remove fields that sttart with FILTER_ADD from request_args, so that they won't be passed to update_config
			for filter_add_argument in list(escaped_request_arguments.keys()):
				if filter_add_argument.startswith('FILTER_ADD'):
					del escaped_request_arguments[filter_add_argument]

			errors = self.update_config(escaped_request_arguments)
			self.restart_ui()
		else:
			errors = {'ZYNTHIAN_MIDI_FILTER_RULES':filterError};
		self.get(errors)

	def validate_filter_rules(self, escaped_request_arguments):
		if escaped_request_arguments['ZYNTHIAN_MIDI_FILTER_RULES'][0]:
			newLine = escaped_request_arguments['ZYNTHIAN_MIDI_FILTER_RULES'][0];
			try:
				mfs = MidiFilterScript(newLine, False)
			except Exception as e:
				return "ERROR parsing MIDI filter rule: " + str(e)
