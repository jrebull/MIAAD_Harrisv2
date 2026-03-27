export const useApi = () => {
  const config = useRuntimeConfig()
  const baseURL = config.public.apiBase as string

  async function get<T = any>(path: string): Promise<T> {
    return await $fetch<T>(path, { baseURL })
  }

  async function post<T = any>(path: string, body: any): Promise<T> {
    return await $fetch<T>(path, { baseURL, method: 'POST', body })
  }

  function wsUrl(path: string): string {
    const wsBase = baseURL.replace(/^http/, 'ws')
    return `${wsBase}${path}`
  }

  return { get, post, wsUrl, baseURL }
}
