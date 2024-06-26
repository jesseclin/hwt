from collections import deque

from hwt.simulator.agentBase import SyncAgentBase
from hwt.synthesizer.exceptions import IntfLvlConfErr
from hwtSimApi.agents.base import AgentBase
from hwtSimApi.constants import CLK_PERIOD
from hwtSimApi.hdlSimulator import HdlSimulator
from hwtSimApi.triggers import Timer, WaitWriteOnly, WaitCombRead, WaitCombStable


class HwIOSignalAgent(SyncAgentBase):
    """
    Agent for signal interface, it can use clock and reset interface
    for synchronization or can be synchronized by delay

    :attention: clock synchronization has higher priority
    """

    def __init__(self, sim: HdlSimulator, hwIO: "HwIOSignal", delay=None):
        AgentBase.__init__(self, sim, hwIO)
        self.delay = delay
        self.initDelay = 0

        # resolve clk and rstn
        try:
            self.clk = self.hwIO._getAssociatedClk()
        except IntfLvlConfErr:
            self.clk = None
        self.rst, self.rstOffIn = self._discoverReset(hwIO, True)
        self.data = deque()

        self.initPending = True
    
        if self.clk is None:
            if self.delay is None:
                self.delay = CLK_PERIOD
            self.monitor = self.monitorWithTimer
            self.driver = self.driverWithTimer
        else:
            if self.initDelay:
                raise NotImplementedError("initDelay only without clock")
            if self.delay:
                raise ValueError("clock and delay synchronization at once")
            c = self.SELECTED_EDGE_CALLBACK
            self.monitor = c(self.sim, self.clk, self.monitorWithClk, self.getEnable)
            self.driver = c(self.sim, self.clk, self.driverWithClk, self.getEnable)

    def getDrivers(self):
        yield self.driverInit()
        if self.clk is None:
            if self.delay is None:
                self.delay = CLK_PERIOD
            yield self.driverWithTimer()
        else:
            if self.initDelay:
                raise NotImplementedError("initDelay only without clock")
            if self.delay:
                raise ValueError("clock and delay synchronization at once")
            c = self.SELECTED_EDGE_CALLBACK
            if not isinstance(self.driver, c):
                self.driver = c(self.sim, self.clk, self.driverWithClk, self.getEnable)
            yield self.driver()
            
    def getMonitors(self):
        if self.clk is None:
            if self.delay is None:
                self.delay = CLK_PERIOD
            yield self.monitorWithTimer()
        else:
            if self.initDelay:
                raise NotImplementedError("initDelay only without clock")
            if self.delay:
                raise ValueError("clock and delay synchronization at once")
            c = self.SELECTED_EDGE_CALLBACK
            if not isinstance(self.monitor, c):
                self.monitor = c(self.sim, self.clk, self.monitorWithClk, self.getEnable)
            yield self.monitor()

    def driverInit(self):
        yield WaitWriteOnly()
        if not self._enabled:
            return
        try:
            d = self.data[0]
        except IndexError:
            d = None

        self.set_data(d)

    def get_data(self):
        return self.hwIO.read()

    def set_data(self, data):
        self.hwIO.write(data)

    def driverWithClk(self):
        # if clock is specified this function is periodically called every
        # clk tick, if agent is enabled
        yield WaitCombRead()
        if not self._enabled:
            return
        if self.data and self.notReset():
            yield WaitWriteOnly()
            if not self._enabled:
                return
            d = self.data.popleft()
            self.set_data(d)

    def driverWithTimer(self):
        if self.initPending:
            if self.initDelay:
                yield Timer(self.initDelay)
            self.initPending = False
        # if clock is specified this function is periodically called every
        # clk tick
        while True:
            yield WaitWriteOnly()
            if self._enabled and self.data and self.notReset():
                yield WaitWriteOnly()
                if self._enabled:
                    d = self.data.popleft()
                    self.set_data(d)

            yield Timer(self.delay)

    def monitorWithTimer(self):
        if self.initPending and self.initDelay:
            yield Timer(self.initDelay)
            self.initPending = False
        # if there is no clk, we have to manage periodic call by our self
        while True:
            yield WaitCombRead()
            if self._enabled and self.notReset():
                d = self.get_data()
                self.data.append(d)

            yield Timer(self.delay)

    def monitorWithClk(self):
        # if clock is specified this function is periodically called every
        # clk tick, when agent is enabled
        yield WaitCombStable()
        if self._enabled and self.notReset():
            d = self.get_data()
            self.data.append(d)
