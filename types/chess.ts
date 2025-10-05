export interface ChessPosition {
    row: number;
    col: number;
}

export interface ChessMove {
    from: ChessPosition;
    to: ChessPosition;
    piece: string;
    captured?: string;
    notation: string;
    timestamp: number;
}

export interface GameState {
    board: string[][];
    currentPlayer: 'white' | 'black';
    selectedSquare: ChessPosition | null;
    moveHistory: ChessMove[];
    gameStatus: 'normal' | 'check' | 'checkmate' | 'stalemate';
    whiteTime: number;
    blackTime: number;
    aiMode: boolean;
    aiThinking: boolean;
}

export interface PlayerInfo {
    name: string;
    time: number;
    isActive: boolean;
}

export const PIECE_SYMBOLS: Record<string, string> = {
    'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',
    'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟'
};

export const INITIAL_BOARD: string[][] = [
    ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
    ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
    ['', '', '', '', '', '', '', ''],
    ['', '', '', '', '', '', '', ''],
    ['', '', '', '', '', '', '', ''],
    ['', '', '', '', '', '', '', ''],
    ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
    ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
];
