import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    exclude: ['lucide-react'],
  },
  build: {
    commonjsOptions: {
      include: [/jspdf/, /jspdf-autotable/],
    },
  },
  // 🌐 Configuração para rede local
  server: {
    host: '0.0.0.0', // Permite acesso de qualquer IP na rede
    port: 5173,      // Porta padrão do Vite
    strictPort: true, // Falha se a porta estiver ocupada
    cors: true,      // Habilita CORS para desenvolvimento
  },
});
