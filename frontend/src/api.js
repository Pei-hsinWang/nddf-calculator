import axios from 'axios'

const API_BASE = '/api'

export const api = {
  async uploadFile(file) {
    const formData = new FormData()
    formData.append('file', file)
    const response = await axios.post(`${API_BASE}/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  },

  async getSheetData(fileId, sheetName) {
    const formData = new FormData()
    formData.append('file_id', fileId)
    formData.append('sheet_name', sheetName)
    const response = await axios.post(`${API_BASE}/sheet-data`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  },

  async compute(config, data) {
    const response = await axios.post(`${API_BASE}/compute`, {
      config,
      data
    })
    return response.data
  },

  async exportResults(config, results) {
    const response = await axios.post(`${API_BASE}/export`, {
      config,
      results
    }, {
      responseType: 'blob'
    })
    return response.data
  },

  async getColumnsInfo() {
    const response = await axios.get(`${API_BASE}/columns-info`)
    return response.data
  }
}
