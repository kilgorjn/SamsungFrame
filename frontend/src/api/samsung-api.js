/**
 * API client for Samsung Frame Art Controller backend
 */
import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const samsungApi = {
  // Health check
  async healthCheck() {
    const { data } = await api.get('/health');
    return data;
  },

  // TV Status
  async getTvStatus() {
    const { data } = await api.get('/tv/status');
    return data;
  },

  async getTvSettings() {
    const { data } = await api.get('/tv/settings');
    return data;
  },

  // Artwork operations
  async getCurrentArtwork() {
    const { data } = await api.get('/art/current');
    return data;
  },

  async getArtworkList() {
    const { data } = await api.get('/art/list');
    return data;
  },

  async selectArtwork(contentId, categoryId = null, show = false) {
    const { data } = await api.post('/art/select', {
      content_id: contentId,
      category_id: categoryId,
      show: show,
    });
    return data;
  },

  async getThumbnail(contentId) {
    try {
      const { data } = await api.get(`/art/thumbnail/${contentId}`, {
        responseType: 'blob',
      });
      return URL.createObjectURL(data);
    } catch (error) {
      if (error.response?.status === 404) {
        // Art Store content not available for download
        return null;
      }
      throw error;
    }
  },

  async uploadArtwork(file, matte = 'shadowbox_polar', portraitMatte = 'shadowbox_polar') {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('matte', matte);
    formData.append('portrait_matte', portraitMatte);

    const { data } = await api.post('/art/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return data;
  },

  async deleteArtwork(contentId) {
    const { data } = await api.delete(`/art/${contentId}`);
    return data;
  },

  async getMatteList() {
    const { data } = await api.get('/art/mattes');
    return data;
  },

  async changeMatte(contentId, matteId, portraitMatteId = null) {
    const { data } = await api.post('/art/matte', {
      content_id: contentId,
      matte_id: matteId,
      portrait_matte_id: portraitMatteId,
    });
    return data;
  },

  async setBrightness(value) {
    const { data } = await api.post('/art/brightness', {
      value: String(value),
    });
    return data;
  },

  async setColorTemperature(value) {
    const { data } = await api.post('/art/color-temperature', {
      value: String(value),
    });
    return data;
  },
};
