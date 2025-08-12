# NovaCorp HR Assistant - Vercel Deployment Guide

## Prerequisites

1. **GitHub Account**: Ensure your code is pushed to GitHub
2. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
3. **Environment Variables**: Set up any required API keys

## Deployment Steps

### 1. Push to GitHub

```bash
git add .
git commit -m "Prepare for Vercel deployment"
git push origin main
```

### 2. Deploy to Vercel

#### Option A: Using Vercel CLI

```bash
npm i -g vercel
vercel --prod
```

#### Option B: Using Vercel Dashboard

1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Click "New Project"
3. Import your GitHub repository
4. Configure settings:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

### 3. Environment Variables (if needed)

In Vercel Dashboard → Project Settings → Environment Variables, add:

- `NODE_ENV` = `production`
- Add any API keys you might need for future enhancements

### 4. Domain Configuration

- Vercel will provide a default domain: `your-project.vercel.app`
- You can configure a custom domain in Project Settings

## Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── api/
│   │   │   └── workflow/
│   │   │       └── route.ts     # Serverless API endpoint
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── components/
│   │   ├── hr-chat-dashboard.tsx
│   │   └── ...
│   └── ...
├── vercel.json                  # Vercel configuration
├── package.json
└── ...
```

## API Routes

The application uses Next.js API routes for serverless functions:

- **Endpoint**: `/api/workflow`
- **Method**: `POST`
- **Payload**: `{ query: string, user_id: string }`

## Local Development

```bash
cd frontend
npm install
npm run dev
```

## Production Features

✅ **Serverless Functions**: No need to manage backend servers
✅ **Auto-scaling**: Vercel handles traffic automatically  
✅ **Global CDN**: Fast loading worldwide
✅ **HTTPS**: SSL certificates included
✅ **Custom Domains**: Easy domain configuration

## Troubleshooting

### Build Errors

- Check Node.js version compatibility
- Ensure all dependencies are installed
- Review build logs in Vercel dashboard

### API Issues

- Check function logs in Vercel dashboard
- Verify API route paths are correct
- Test API endpoints locally first

### Environment Variables

- Ensure all required env vars are set in Vercel
- Check variable names match exactly

## Future Enhancements

To integrate with actual RAG workflow:

1. Add Pinecone/vector database integration
2. Add OpenAI/LLM API integration
3. Implement document processing pipeline
4. Add authentication system

## Support

For deployment issues:

- Check [Vercel Documentation](https://vercel.com/docs)
- Review build and function logs
- Test locally before deploying
