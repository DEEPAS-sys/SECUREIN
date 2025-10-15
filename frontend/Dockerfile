FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application code
COPY . .

# Build application
# RUN npm run build

# Expose port
EXPOSE 3000

# Development mode
CMD ["npm", "run", "dev"]

# Production mode
# CMD ["npm", "run", "preview"]
