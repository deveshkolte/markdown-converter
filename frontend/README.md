# Next.js Frontend

Deployed at `https://markitdown-web.vercel.app`.

## Local dev

```bash
npm install
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

Open `http://localhost:3000`.

## Environment

| Variable | Required | Description |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | Yes | FastAPI backend URL (e.g. `https://markdown-converter-0jsu.onrender.com`) |

See [root README](/README.md#web-ui) for usage.
