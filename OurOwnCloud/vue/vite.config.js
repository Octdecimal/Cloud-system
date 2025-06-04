import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
	plugins: [vue()],
	server: {
		port: 5173,
		proxy: {
			'/upload':    { target: 'http://localhost:8000', changeOrigin: true },
			'/status':    { target: 'http://localhost:8000', changeOrigin: true },
			'/uploads':   { target: 'http://localhost:8000', changeOrigin: true },
			// 如果還有 /node_usage、/favicon.ico… 也可以一併 proxy
		}
	}
})
