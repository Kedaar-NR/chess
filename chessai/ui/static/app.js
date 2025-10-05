// ChessAI Engine Frontend JavaScript

class ChessBoard {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.squareSize = 50;
        this.boardSize = 8 * this.squareSize;
        this.flipped = false;
        this.selectedSquare = null;
        this.highlightedSquares = [];
        this.pieces = {};
        this.position = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';
        this.moveHistory = [];
        
        this.initializeBoard();
        this.drawBoard();
    }
    
    initializeBoard() {
        // Set canvas size
        this.canvas.width = this.boardSize;
        this.canvas.height = this.boardSize;
        
        // Add click event listener
        this.canvas.addEventListener('click', (e) => this.handleClick(e));
    }
    
    handleClick(event) {
        const rect = this.canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        
        const square = this.getSquareFromCoords(x, y);
        if (square) {
            this.onSquareClick(square);
        }
    }
    
    getSquareFromCoords(x, y) {
        const col = Math.floor(x / this.squareSize);
        const row = Math.floor(y / this.squareSize);
        
        if (col >= 0 && col < 8 && row >= 0 && row < 8) {
            const file = String.fromCharCode(97 + col); // a-h
            const rank = 8 - row;
            return file + rank;
        }
        return null;
    }
    
    onSquareClick(square) {
        if (this.selectedSquare === square) {
            this.selectedSquare = null;
        } else if (this.selectedSquare) {
            // Try to make a move
            const move = this.selectedSquare + square;
            this.makeMove(move);
            this.selectedSquare = null;
        } else {
            this.selectedSquare = square;
        }
        this.drawBoard();
    }
    
    makeMove(move) {
        // TODO: Validate move and update position
        console.log('Move:', move);
        this.moveHistory.push(move);
        this.updateMoveList();
    }
    
    drawBoard() {
        this.ctx.clearRect(0, 0, this.boardSize, this.boardSize);
        
        // Draw squares
        for (let row = 0; row < 8; row++) {
            for (let col = 0; col < 8; col++) {
                const isLight = (row + col) % 2 === 0;
                const x = col * this.squareSize;
                const y = row * this.squareSize;
                
                // Draw square
                this.ctx.fillStyle = isLight ? '#f0d9b5' : '#b58863';
                this.ctx.fillRect(x, y, this.squareSize, this.squareSize);
                
                // Highlight selected square
                if (this.selectedSquare) {
                    const square = this.getSquareFromCoords(x + this.squareSize/2, y + this.squareSize/2);
                    if (square === this.selectedSquare) {
                        this.ctx.fillStyle = 'rgba(255, 255, 0, 0.5)';
                        this.ctx.fillRect(x, y, this.squareSize, this.squareSize);
                    }
                }
                
                // Draw piece
                this.drawPiece(row, col);
            }
        }
        
        // Draw coordinates
        this.drawCoordinates();
    }
    
    drawPiece(row, col) {
        // TODO: Implement piece drawing
        // This is a placeholder - in a real implementation, you would draw actual piece symbols
    }
    
    drawCoordinates() {
        this.ctx.fillStyle = '#333';
        this.ctx.font = '12px Arial';
        
        for (let i = 0; i < 8; i++) {
            // Files (a-h)
            this.ctx.fillText(String.fromCharCode(97 + i), i * this.squareSize + 2, this.boardSize - 2);
            // Ranks (1-8)
            this.ctx.fillText((8 - i).toString(), 2, i * this.squareSize + 12);
        }
    }
    
    flipBoard() {
        this.flipped = !this.flipped;
        this.drawBoard();
    }
    
    newGame() {
        this.position = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';
        this.moveHistory = [];
        this.selectedSquare = null;
        this.updateMoveList();
        this.updateFenDisplay();
        this.drawBoard();
    }
    
    updateMoveList() {
        const moveList = document.getElementById('moveList');
        moveList.innerHTML = '';
        
        this.moveHistory.forEach((move, index) => {
            const moveItem = document.createElement('div');
            moveItem.className = 'move-item';
            moveItem.textContent = `${index + 1}. ${move}`;
            moveList.appendChild(moveItem);
        });
    }
    
    updateFenDisplay() {
        document.getElementById('fenDisplay').textContent = `FEN: ${this.position}`;
    }
}

class ChessAPI {
    constructor(baseUrl = '') {
        this.baseUrl = baseUrl;
    }
    
    async analyzePosition(fen, timeLimit = 5) {
        try {
            const response = await fetch(`${this.baseUrl}/analyse`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    fen: fen,
                    time_limit: timeLimit
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error analyzing position:', error);
            throw error;
        }
    }
    
    async getBestMove(fen, timeLimit = 5) {
        try {
            const response = await fetch(`${this.baseUrl}/bestmove`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    fen: fen,
                    time_limit: timeLimit
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error getting best move:', error);
            throw error;
        }
    }
    
    async getHealth() {
        try {
            const response = await fetch(`${this.baseUrl}/health`);
            return await response.json();
        } catch (error) {
            console.error('Error getting health:', error);
            throw error;
        }
    }
}

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    const board = new ChessBoard('chessBoard');
    const api = new ChessAPI();
    
    // Event listeners
    document.getElementById('newGame').addEventListener('click', () => {
        board.newGame();
    });
    
    document.getElementById('flipBoard').addEventListener('click', () => {
        board.flipBoard();
    });
    
    document.getElementById('analyzeBtn').addEventListener('click', async () => {
        const timeLimit = parseFloat(document.getElementById('timeLimit').value);
        
        try {
            document.getElementById('analyzeBtn').textContent = 'Analyzing...';
            document.getElementById('analyzeBtn').disabled = true;
            
            const result = await api.analyzePosition(board.position, timeLimit);
            
            // Update display
            document.getElementById('score').textContent = `Score: ${result.score.toFixed(3)}`;
            document.getElementById('centipawns').textContent = `Centipawns: ${result.centipawns}`;
            document.getElementById('nodes').textContent = `Nodes: ${result.nodes}`;
            document.getElementById('depth').textContent = `Depth: ${result.depth}`;
            document.getElementById('time').textContent = `Time: ${result.time_ms}ms`;
            
            // Update PV
            const pvMoves = document.getElementById('pvMoves');
            pvMoves.textContent = result.pv.join(' ');
            
        } catch (error) {
            console.error('Analysis failed:', error);
            alert('Analysis failed: ' + error.message);
        } finally {
            document.getElementById('analyzeBtn').textContent = 'Analyze Position';
            document.getElementById('analyzeBtn').disabled = false;
        }
    });
    
    document.getElementById('bestMoveBtn').addEventListener('click', async () => {
        const timeLimit = parseFloat(document.getElementById('timeLimit').value);
        
        try {
            document.getElementById('bestMoveBtn').textContent = 'Thinking...';
            document.getElementById('bestMoveBtn').disabled = true;
            
            const result = await api.getBestMove(board.position, timeLimit);
            
            // Update display
            document.getElementById('score').textContent = `Score: ${result.score.toFixed(3)}`;
            document.getElementById('centipawns').textContent = `Centipawns: ${result.centipawns}`;
            document.getElementById('nodes').textContent = `Nodes: ${result.nodes}`;
            document.getElementById('time').textContent = `Time: ${result.time_ms}ms`;
            
            // Show best move
            if (result.bestmove) {
                alert(`Best move: ${result.bestmove}`);
            }
            
        } catch (error) {
            console.error('Best move failed:', error);
            alert('Best move failed: ' + error.message);
        } finally {
            document.getElementById('bestMoveBtn').textContent = 'Best Move';
            document.getElementById('bestMoveBtn').disabled = false;
        }
    });
    
    // Check API health on load
    api.getHealth().then(health => {
        console.log('API Health:', health);
    }).catch(error => {
        console.error('API Health check failed:', error);
    });
});
