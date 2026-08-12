FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./
RUN npm ci

# Copy source
COPY . .

# Setting NEXT_PUBLIC_API_URL can be done at build time or runtime if using Next.js runtime config,
# but for standard Next.js static generation, it needs to be available at build time.
# SWR calls happen client-side, so NEXT_PUBLIC_API_URL is injected there.
RUN npm run build

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["npm", "run", "start"]
