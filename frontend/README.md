# Banta Dashboard Frontend

A modern, responsive React dashboard for the Banta CSV data analysis platform.

## Features

- 🎨 **Modern UI/UX** - Clean, intuitive interface built with Tailwind CSS
- 📊 **Interactive Dashboard** - Real-time statistics and data visualization
- 📤 **File Upload** - Drag & drop CSV file upload with progress tracking
- 🤖 **AI Integration** - Question interface for intelligent data analysis
- 📈 **Analytics** - Comprehensive data analytics and insights
- ⚙️ **Settings** - Customizable user preferences and configuration
- 🎭 **Animations** - Smooth transitions and micro-interactions with Framer Motion
- 📱 **Responsive** - Works seamlessly on desktop, tablet, and mobile devices

## Tech Stack

- **React 18** - Modern React with hooks and functional components
- **Vite** - Fast build tool and development server
- **Tailwind CSS** - Utility-first CSS framework for rapid UI development
- **Framer Motion** - Production-ready motion library for React
- **React Router** - Declarative routing for React applications
- **Axios** - HTTP client for API communication
- **React Dropzone** - File upload with drag & drop functionality
- **React Hot Toast** - Beautiful notifications
- **Lucide React** - Beautiful & consistent icon library

## Quick Start

### Prerequisites

- Node.js 18+ 
- npm or yarn package manager

### Installation

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
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
   Visit `http://localhost:3000`

### Build for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

## Project Structure

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── components/        # Reusable UI components
│   │   ├── Sidebar.jsx
│   │   ├── StatsCard.jsx
│   │   ├── ChartCard.jsx
│   │   ├── QuestionInterface.jsx
│   │   └── RecentActivity.jsx
│   ├── pages/             # Page components
│   │   ├── Dashboard.jsx
│   │   ├── DataUpload.jsx
│   │   ├── Analytics.jsx
│   │   └── Settings.jsx
│   ├── utils/             # Utility functions
│   │   ├── api.js         # API client and endpoints
│   │   └── cn.js          # Class name utility
│   ├── App.jsx            # Main application component
│   ├── main.jsx           # Application entry point
│   └── index.css          # Global styles and Tailwind imports
├── package.json
├── vite.config.js
├── tailwind.config.js
└── README.md
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally
- `npm run lint` - Run ESLint for code quality

## API Integration

The frontend is configured to work with the FastAPI backend through a proxy setup in Vite. All API calls are made to `/api/*` which are proxied to `http://localhost:8000`.

### Backend Connection

Make sure your FastAPI backend is running on `http://localhost:8000` before starting the frontend development server.

### Key API Endpoints

- `GET /api/health` - Health check
- `POST /api/upload-csv` - Upload CSV files
- `GET /api/list-files` - List uploaded files
- Future endpoints for AI analysis and reporting

## Features Overview

### Dashboard
- Real-time statistics and metrics
- AI-powered question interface
- Recent activity feed
- Data visualization charts
- Welcome messaging and onboarding

### Data Upload
- Drag & drop file upload interface
- Multiple file selection
- Upload progress tracking
- File validation and error handling
- Upload guidelines and help text

### Analytics
- Comprehensive data analytics
- Time-range filtering
- Export functionality
- Key insights and trends
- Interactive charts and graphs

### Settings
- User profile management
- Security settings
- Notification preferences
- Data & storage management
- Appearance customization

## Customization

### Theming

The application uses Tailwind CSS with a custom color palette. To modify the theme:

1. Edit `tailwind.config.js`
2. Update color variables in the `extend.colors` section
3. Customize fonts, animations, and other design tokens

### Adding New Pages

1. Create a new component in `src/pages/`
2. Add the route to `src/App.jsx`
3. Update navigation in `src/components/Sidebar.jsx`

### API Configuration

Update API endpoints and configuration in `src/utils/api.js`:

- Base URL configuration
- Request/response interceptors
- Error handling
- Authentication headers

## Performance Optimization

- **Code Splitting** - React Router automatically splits code by routes
- **Lazy Loading** - Components are loaded on demand
- **Image Optimization** - Use WebP format and proper sizing
- **Bundle Analysis** - Use `npm run build` to analyze bundle size
- **Caching** - Browser caching for static assets

## Browser Support

- Chrome/Chromium 88+
- Firefox 85+
- Safari 14+
- Edge 88+

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.
