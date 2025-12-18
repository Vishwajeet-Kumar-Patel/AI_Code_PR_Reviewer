# AI-Powered Code Review Frontend

Next.js 14 application with TypeScript for the AI Code Review System.

## Features

- 🎨 Modern UI with Tailwind CSS
- 📊 Real-time PR analysis dashboard
- 🔍 Detailed code review insights
- 🎯 Issue tracking and recommendations
- 📈 Quality, Security, and Complexity scores
- 🌙 Dark mode by default
- ⚡ Fast refresh and hot module replacement

## Tech Stack

- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **State Management:** Zustand
- **Data Fetching:** SWR + Axios
- **Code Highlighting:** React Syntax Highlighter
- **Icons:** Lucide React
- **Date Formatting:** date-fns

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm/yarn/pnpm

### Installation

```bash
# Install dependencies
npm install

# Set up environment variables
cp .env.local.example .env.local
# Edit .env.local with your configuration

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the application.

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── dashboard/         # Dashboard page
│   │   ├── pr/                # PR detail pages
│   │   ├── layout.tsx         # Root layout
│   │   ├── page.tsx           # Home page (redirects to dashboard)
│   │   └── globals.css        # Global styles
│   ├── components/            # React components
│   │   ├── Layout.tsx         # Main layout with sidebar
│   │   ├── Sidebar.tsx        # Navigation sidebar
│   │   ├── Header.tsx         # Top header with search
│   │   ├── PRCard.tsx         # PR list item card
│   │   └── IssueCard.tsx      # Issue display card
│   ├── lib/                   # Utility libraries
│   │   └── api-client.ts      # API client for backend
│   └── types/                 # TypeScript type definitions
│       └── index.ts           # Shared types
├── public/                    # Static assets
├── package.json              # Dependencies
├── tsconfig.json             # TypeScript config
├── tailwind.config.js        # Tailwind CSS config
├── next.config.js            # Next.js config
└── postcss.config.js         # PostCSS config
```

## Available Scripts

```bash
# Development
npm run dev          # Start dev server at localhost:3000

# Production
npm run build        # Build for production
npm run start        # Start production server

# Code Quality
npm run lint         # Run ESLint
npm run type-check   # Run TypeScript compiler check
```

## Environment Variables

Create a `.env.local` file:

```env
# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_VERSION=v1

# Database (for server-side operations)
DATABASE_URL=postgresql://postgres:password@localhost:5432/ai_code_review

# GitHub OAuth (optional)
GITHUB_CLIENT_ID=your_client_id
GITHUB_CLIENT_SECRET=your_client_secret
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your_secret
```

## Key Features

### Dashboard
- List all pull requests with filters
- Real-time status updates
- Quick access to PR analysis
- Repository and status filtering

### PR Detail View
- Comprehensive PR information
- Quality, Security, and Complexity scores
- Detailed issue breakdown
- File-by-file analysis
- Code snippets with syntax highlighting
- Actionable recommendations

### Components

#### Layout
Main application layout with sidebar navigation and header.

#### PRCard
Displays PR summary with metadata, author, status, and review scores.

#### IssueCard
Shows individual code issues with:
- Issue type and severity
- Code snippet
- Detailed description
- Recommended fixes

## API Integration

The frontend communicates with the FastAPI backend via the `apiClient`:

```typescript
import apiClient from '@/lib/api-client';

// Analyze a PR
const review = await apiClient.analyzePR({
  repository_owner: 'owner',
  repository_name: 'repo',
  pull_request_number: 123,
});

// Get review details
const review = await apiClient.getReview(reviewId);

// List PRs
const prs = await apiClient.listPullRequests({
  status: 'open',
  sort: 'newest',
});
```

## Styling

The application uses Tailwind CSS with a custom dark theme:

```css
/* Custom colors */
primary: Blue shades for accents
dark: Dark grays for backgrounds

/* Components */
.badge: Small status indicators
.code-block: Code snippet container
```

## Type Safety

All API responses are fully typed:

```typescript
interface Review {
  id: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  quality_score?: number;
  security_score?: number;
  file_analyses?: FileAnalysis[];
  // ...
}
```

## Performance

- **Server Components:** Used by default for optimal performance
- **Client Components:** Only where interactivity is needed
- **Code Splitting:** Automatic route-based code splitting
- **Image Optimization:** Next.js Image component
- **Bundle Size:** Optimized with SWC compiler

## Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Docker

```bash
# Build image
docker build -t ai-code-review-frontend .

# Run container
docker run -p 3000:3000 ai-code-review-frontend
```

### Manual

```bash
# Build
npm run build

# Start
npm run start
```

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## Troubleshooting

### Port 3000 already in use

```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID <process_id> /F

# Or use a different port
npm run dev -- -p 3001
```

### API connection errors

1. Verify backend is running at http://localhost:8000
2. Check NEXT_PUBLIC_API_URL in .env.local
3. Check CORS settings in backend

### Build errors

```bash
# Clear Next.js cache
rm -rf .next

# Reinstall dependencies
rm -rf node_modules
npm install

# Try building again
npm run build
```

## License

MIT

## Support

For issues and questions:
- Backend API: http://localhost:8000/docs
- Logs: Check browser console and Network tab
- GitHub Issues: [Your repo URL]
