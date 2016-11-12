import unittest
from unittest.mock import MagicMock

from banks_manager import BanksManager

from model.bank import Bank
from model.connection import Connection
from model.patch import Patch
from model.update_type import UpdateType

from model.lv2.lv2_effect_builder import Lv2EffectBuilder


class BanksManagerTest(unittest.TestCase):

    def test_observers(self):
        manager = BanksManager()
        observer = MagicMock()

        bank = Bank('Bank 1')
        manager.append(bank)

        manager.register(observer)

        patch = Patch('Rocksmith')
        bank.append(patch)

        observer.on_patch_updated.assert_called_with(patch, UpdateType.CREATED, None)

        builder = Lv2EffectBuilder()
        reverb = builder.build('http://calf.sourceforge.net/plugins/Reverb')
        fuzz = builder.build('http://guitarix.sourceforge.net/plugins/gx_fuzzfacefm_#_fuzzfacefm_')
        reverb2 = builder.build('http://calf.sourceforge.net/plugins/Reverb')

        patch.append(reverb)
        observer.on_effect_updated.assert_called_with(reverb, UpdateType.CREATED, None)
        patch.append(fuzz)
        observer.on_effect_updated.assert_called_with(fuzz, UpdateType.CREATED, None)
        patch.append(reverb2)
        observer.on_effect_updated.assert_called_with(reverb2, UpdateType.CREATED, None)

        reverb.outputs[0].connect(fuzz.inputs[0])
        observer.on_connection_updated.assert_called_with(
            Connection(reverb.outputs[0], fuzz.inputs[0]),
            UpdateType.CREATED,
            None
        )
        reverb.outputs[1].connect(fuzz.inputs[0])
        observer.on_connection_updated.assert_called_with(
            Connection(reverb.outputs[1], fuzz.inputs[0]),
            UpdateType.CREATED,
            None
        )
        fuzz.outputs[0].connect(reverb2.inputs[0])
        observer.on_connection_updated.assert_called_with(
            Connection(fuzz.outputs[0], reverb2.inputs[0]),
            UpdateType.CREATED,
            None
        )
        reverb.outputs[0].connect(reverb2.inputs[0])
        observer.on_connection_updated.assert_called_with(
            Connection(reverb.outputs[0], reverb2.inputs[0]),
            UpdateType.CREATED,
            None
        )

        fuzz.toggle()
        observer.on_effect_status_toggled.assert_called_with(fuzz, None)

        fuzz.params[0].value = fuzz.params[0].minimum / fuzz.params[0].maximum
        observer.on_param_value_changed.assert_called_with(fuzz.params[0], None)
