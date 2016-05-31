from hdl_toolkit.synthetisator.interfaceLevel.interface import Interface
from hdl_toolkit.synthetisator.param import Param
from hdl_toolkit.interfaces.amba import AxiStream
from hdl_toolkit.hdlObjects.specialValues import DIRECTION


class FullDuplexAxiStream(Interface):
    def _config(self):
        self.DATA_WIDTH = Param(64)
    
    def _declr(self):
        self.tx = AxiStream()
        self.rx = AxiStream(masterDir=DIRECTION.IN)
        self._shareAllParams()