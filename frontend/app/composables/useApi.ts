export const useApi = () => {
  const config = useRuntimeConfig()
  const baseURL = config.public.apiBase as string

  async function get<T = any>(path: string): Promise<T> {
    try {
      return await $fetch<T>(path, { baseURL, retry: 1, retryDelay: 500 })
    } catch (err: any) {
      const status = err?.response?.status || err?.statusCode
      const msg = err?.data?.detail || err?.message || 'Error de conexión con el servidor'
      console.error(`[API GET ${path}]`, status, msg)
      throw new Error(msg)
    }
  }

  async function post<T = any>(path: string, body: any): Promise<T> {
    try {
      return await $fetch<T>(path, { baseURL, method: 'POST', body })
    } catch (err: any) {
      const msg = err?.data?.detail || err?.message || 'Error en la petición'
      console.error(`[API POST ${path}]`, msg)
      throw new Error(msg)
    }
  }

  function wsUrl(path: string): string {
    const wsBase = baseURL.replace(/^http/, 'ws')
    return `${wsBase}${path}`
  }

  return { get, post, wsUrl, baseURL }
}
