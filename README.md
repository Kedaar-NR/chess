# Chess Engine - Next.js TypeScript

A modern, interactive chess engine built with Next.js, TypeScript, and Tailwind CSS. Features a beautiful web interface with AI gameplay, move logging, and real-time timers.

## 🎯 Features

- **Interactive Chess Board** - Click pieces to move them with smooth animations
- **AI vs AI Mode** - Watch two intelligent bots play against each other
- **Real-time Timers** - Track time for each player with live updates
- **Move Logging** - Complete move history with algebraic notation
- **Beautiful UI** - Modern design with responsive layout
- **TypeScript** - Full type safety and excellent developer experience
- **Mobile Friendly** - Works perfectly on desktop and mobile devices

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- npm or yarn

### Installation

1. **Clone and navigate to the project:**
   ```bash
   cd chess-bot
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

4. **Open your browser:**
   Visit [http://localhost:3000](http://localhost:3000) (or the port shown in terminal)

## 🎮 How to Play

### Basic Gameplay
1. **Click a piece** to select it (highlighted in blue)
2. **Click a destination square** to move the piece
3. **Use the control buttons** to manage the game

### Game Modes
- **Human vs AI**: Click pieces to move, use "AI Move" for computer moves
- **AI vs AI**: Click "AI vs AI" to watch two bots play automatically
- **New Game**: Start a fresh game with reset board
- **Undo**: Undo the last move made

### Controls
- **New Game** - Reset the board to starting position
- **AI Move** - Make the AI play one move
- **AI vs AI** - Start automatic bot vs bot gameplay
- **Undo** - Undo the last move

## 🏗️ Project Structure

```
├── app/
│   ├── globals.css          # Global styles with Tailwind
│   ├── layout.tsx           # Root layout component
│   └── page.tsx             # Main chess game page
├── components/
│   ├── ChessBoard.tsx       # Interactive chess board
│   ├── GameControls.tsx     # Game control buttons
│   ├── GameStatus.tsx       # Game status display
│   ├── MoveLog.tsx          # Move history component
│   └── PlayerInfo.tsx       # Player information cards
├── hooks/
│   └── useChessGame.ts      # Chess game logic and state
├── types/
│   └── chess.ts             # TypeScript type definitions
├── package.json             # Dependencies and scripts
├── tailwind.config.js       # Tailwind CSS configuration
└── tsconfig.json            # TypeScript configuration
```

## 🛠️ Technologies Used

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe JavaScript development
- **Tailwind CSS** - Utility-first CSS framework
- **React Hooks** - Modern state management
- **Lucide React** - Beautiful, consistent icons
- **Custom Game Logic** - Chess rules and AI implementation

## 🎨 Key Features

### Chess Board
- 8x8 grid with proper light/dark square colors
- Unicode chess piece symbols (♔♕♖♗♘♙)
- Click to select and move pieces
- Visual feedback for selected pieces and last moves
- Smooth hover and click animations

### Game Logic
- Move validation and turn management
- Complete move history tracking
- Real-time timer management
- AI move generation with smart tactics
- Game state management (check, checkmate, stalemate)

### UI Components
- Responsive design that works on all devices
- Beautiful animations and transitions
- Real-time updates without page refresh
- Accessible controls and keyboard support
- Professional typography and spacing

## 🔧 Development

### Available Scripts

```bash
npm run dev      # Start development server
npm run build    # Build for production
npm run start    # Start production server
npm run lint     # Run ESLint for code quality
```

### Customization

**Styling**: Edit `tailwind.config.js` to customize colors and animations:
```javascript
theme: {
  extend: {
    colors: {
      'chess-light': '#f0d9b5',
      'chess-dark': '#b58863',
      // Add your custom colors
    }
  }
}
```

**Game Logic**: Modify `hooks/useChessGame.ts` to change AI behavior:
```typescript
// Customize AI move selection
const makeAIMove = useCallback(() => {
  // Add your AI logic here
}, []);
```

## 📱 Deployment

### Vercel (Recommended)
1. Push your code to GitHub
2. Connect your repository to Vercel
3. Deploy automatically with zero configuration

### Other Platforms
```bash
npm run build
npm run start
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and test thoroughly
4. Commit your changes: `git commit -m 'Add amazing feature'`
5. Push to the branch: `git push origin feature/amazing-feature`
6. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Chess piece symbols from Unicode
- Icons from Lucide React
- Styling inspiration from modern chess applications
- Built with love for the chess community

---

**Enjoy playing chess!** ♟️

*Built with Next.js, TypeScript, and Tailwind CSS*
<!-- noop: README touch -->