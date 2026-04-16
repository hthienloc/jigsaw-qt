import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QPointF
from board import JigsawBoard

def verify_puzzle_logic():
    # Need a dummy app to use QPixmap/QImage
    app = QApplication(sys.argv)
    
    board = JigsawBoard()
    sample_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "samples", "nature", "nature1.png")
    
    if not os.path.exists(sample_path):
        print("Sample image not found for test.")
        return False

    print(f"Loading image: {sample_path}")
    board.load_image(sample_path)
    
    total_pieces = len(board.pieces)
    print(f"Total pieces generated: {total_pieces}")
    
    if total_pieces == 0:
        print("FAIL: No pieces generated.")
        return False

    # Test Completion Percentage
    completion = board.get_completion_percentage()
    print(f"Initial completion: {completion}%")
    if completion != 0:
        print("FAIL: Initial completion should be 0.")
        return False

    # Test Snapping
    first_piece = board.pieces[0]
    original_pos = first_piece.pos()
    first_piece.setPos(first_piece.correct_pos)
    board._snap_piece_to_board(first_piece)
    
    completion = board.get_completion_percentage()
    print(f"Update completion after 1 snap: {completion}%")
    if completion == 0:
        print("FAIL: Completion should have increased.")
        return False
    if not first_piece.is_locked:
        print("FAIL: Piece should be locked after snap.")
        return False

    # Test Edge Filter
    board.is_edge_filter_active = True
    board._repack_tray()
    
    # Calculate expected edge pieces
    # rows * cols = total
    # edges = 2*rows + 2*cols - 4
    expected_edges = 2 * board.rows + 2 * board.cols - 4
    visible_pieces = sum(1 for p in board.pieces if p.isVisible() and p.is_in_tray)
    # Some pieces might not be in tray if they are locked
    locked_in_tray = sum(1 for p in board.pieces if p.is_locked and p.isVisible() and p.is_in_tray)
    
    print(f"Visible edge pieces in tray: {visible_pieces}")
    # This is a bit complex to assert exactly without knowing piece states, but it should be > 0
    if visible_pieces == 0:
        # Check if they are maybe all locked?
        if any(not p.is_locked for p in board.pieces if (p.row == 0 or p.row == board.rows-1 or p.col == 0 or p.col == board.cols-1)):
             print("FAIL: Edge pieces should be visible.")
             return False

    # Test Adjacency Snap Restriction
    # Piece (0,0) and (2,2) are not adjacent. 
    # Move (2,2) near where it would be relative to (0,0) if they WERE neighbors physically
    # (Actually, just move them to their relative correct positions but far apart in grid)
    if total_pieces > 10:
        p00 = next(p for p in board.pieces if p.row == 0 and p.col == 0)
        p22 = next(p for p in board.pieces if p.row == 2 and p.col == 2)
        
        # Move p00 AWAY from its correct position
        p00.setPos(QPointF(500, 500))
        p00.is_in_tray = False # Move to board area
        
        # Move p22 to its correct relative position to p00 but FAR from its own correct pos
        rel_correct = p22.correct_pos - p00.correct_pos
        p22.setPos(p00.pos() + rel_correct)
        p22.is_in_tray = False

        # Manually trigger release logic
        board.clearSelection()
        p22.setSelected(True)
        board.mouseReleaseEvent(None) 
        
        if p22.cluster == p00.cluster or p22.is_locked:
            print("FAIL: Non-adjacent pieces (0,0) and (2,2) snapped together!")
            return False
        else:
            print("SUCCESS: Non-adjacent pieces did not snap.")

    print("ALL LOGIC CHECKS PASSED.")
    return True

if __name__ == "__main__":
    if verify_puzzle_logic():
        sys.exit(0)
    else:
        sys.exit(1)
