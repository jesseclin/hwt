from typing import Set, List, Dict, Optional, Callable

from hwt.doc_markers import internal
from hwt.hdl.statements.assignmentContainer import HdlAssignmentContainer
from hwt.hdl.statements.statement import HdlStatement
from hwt.hdl.statements.utils.listOfHdlStatements import ListOfHdlStatement
from hwt.mainBases import RtlSignalBase


class HdlAssignmentContainer_constructor():

    def __init__(self, src, dst):
        self.dst = dst
        self.src = src

    def __call__(self) -> HdlAssignmentContainer:
        return HdlAssignmentContainer(self.src, self.dst)


@internal
def fill_stm_list_with_enclosure(parentStm: Optional[HdlStatement],
                                 current_enclosure: Set[RtlSignalBase],
                                 statements: ListOfHdlStatement,
                                 do_enclose_for: List[RtlSignalBase],
                                 enclosure: Dict[RtlSignalBase, Callable[[], HdlStatement]])\
        ->ListOfHdlStatement:
    """
    Apply enclosure on list of statements
    (fill all unused code branches with assignments from value specified by enclosure)

    :param parentStm: optional parent statement where this list is some branch
    :param current_enclosure: list of signals for which this statement list is enclosed
    :param statements: list of statements
    :param do_enclose_for: selected signals for which enclosure should be used
    :param enclosure: enclosure values for signals

    :attention: original statements parameter can be modified
    :return: new statements
    """
    assert do_enclose_for
    if statements is None:
        statements = ListOfHdlStatement()

    for e_sig in do_enclose_for:
        if e_sig in current_enclosure:
            continue
        enclosed = False
        for stm in statements.iterStatementsWithOutput(e_sig):
            if e_sig not in stm._enclosed_for:
                stm._fill_enclosure(enclosure)
            enclosed = True
            break
        # any statement was not related with this signal,
        if not enclosed:
            e = enclosure[e_sig]
            a: HdlStatement = e()
            assert isinstance(a, HdlStatement), a
            statements.append(a)

            if parentStm is not None:
                a._set_parent_stm(parentStm, statements)

    return statements
