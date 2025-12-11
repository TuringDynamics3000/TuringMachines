# TuringCapture™ UI

Mobile-first identity verification interface for TuringCapture.

## Features

✅ **Mobile-First Design** - Optimized for smartphone capture  
✅ **Camera Integration** - Browser-based selfie capture  
✅ **ID Upload** - Front and back document upload  
✅ **Real-time Progress** - Visual feedback during verification  
✅ **Production Ready** - TypeScript, Next.js 14, React 18  

## Quick Start

### Development

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Open http://localhost:3001
```

### Production Build

```bash
# Build for production
npm run build

# Start production server
npm start
```

## Architecture

```
ui/
├── src/
│   ├── pages/          # Next.js pages
│   │   ├── index.tsx   # Landing page
│   │   ├── id.tsx      # ID upload
│   │   ├── selfie.tsx  # Selfie capture
│   │   ├── review.tsx  # Processing
│   │   └── success.tsx # Completion
│   ├── components/     # React components
│   │   ├── MobileLayout.tsx
│   │   ├── CameraCapture.tsx
│   │   └── UploadBox.tsx
│   └── lib/
│       └── api.ts      # Backend integration
├── public/             # Static assets
└── package.json
```

## API Integration

The UI connects to the TuringCapture backend at `http://localhost:8101` by default.

Configure via environment variable:
```bash
NEXT_PUBLIC_API_BASE=https://api.turingmachines.io
```

## Deployment

### Vercel (Recommended)
```bash
vercel deploy
```

### Docker
```bash
docker build -t turing-capture-ui .
docker run -p 3001:3001 turing-capture-ui
```

### Static Export
```bash
npm run build
# Deploy the .next/ directory
```

## Browser Support

- ✅ Chrome/Edge 90+
- ✅ Safari 14+
- ✅ Firefox 88+
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

## Security

- Camera access requires HTTPS in production
- CORS configured for backend integration
- No sensitive data stored in browser

## License

Proprietary - TuringMachines™ Platform
