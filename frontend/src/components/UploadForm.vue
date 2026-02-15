<template>
  <div class="container">
    <h2>Upload New Artwork</h2>

    <form @submit.prevent="handleUpload" style="max-width: 500px;">
      <div style="margin-bottom: 16px;">
        <label style="display: block; margin-bottom: 8px; font-weight: 500;">
          Select Image
        </label>
        <input
          type="file"
          accept="image/*"
          @change="handleFileSelect"
          ref="fileInput"
          style="width: 100%;"
        />
        <p v-if="selectedFile" style="margin-top: 8px; font-size: 14px; color: #666;">
          Selected: {{ selectedFile.name }} ({{ formatFileSize(selectedFile.size) }})
        </p>
      </div>

      <div style="margin-bottom: 16px;">
        <label style="display: block; margin-bottom: 8px; font-weight: 500;">
          Matte Style
        </label>
        <select v-model="matte" style="width: 100%;">
          <option value="none">None</option>
          <option value="shadowbox_polar">Shadowbox Polar (White)</option>
          <option value="modern_polar">Modern Polar (White)</option>
          <option value="shadowbox_sand">Shadowbox Sand (Beige)</option>
          <option value="modern_sand">Modern Sand (Beige)</option>
        </select>
      </div>

      <button type="submit" :disabled="!selectedFile || uploading" style="width: 100%;">
        {{ uploading ? 'Uploading...' : 'Upload to TV' }}
      </button>
    </form>

    <div v-if="successMessage" class="success">{{ successMessage }}</div>
    <div v-if="error" class="error">{{ error }}</div>
  </div>
</template>

<script>
import { ref } from 'vue';
import { samsungApi } from '../api/samsung-api';

export default {
  name: 'UploadForm',
  emits: ['uploadComplete'],
  setup(props, { emit }) {
    const selectedFile = ref(null);
    const matte = ref('shadowbox_polar');
    const uploading = ref(false);
    const successMessage = ref(null);
    const error = ref(null);
    const fileInput = ref(null);

    const handleFileSelect = (event) => {
      const file = event.target.files[0];
      if (file) {
        selectedFile.value = file;
        error.value = null;
      }
    };

    const formatFileSize = (bytes) => {
      if (bytes < 1024) return bytes + ' B';
      if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
      return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    };

    const handleUpload = async () => {
      if (!selectedFile.value) {
        error.value = 'Please select a file';
        return;
      }

      uploading.value = true;
      error.value = null;
      successMessage.value = null;

      try {
        const result = await samsungApi.uploadArtwork(
          selectedFile.value,
          matte.value,
          matte.value // Use same matte for portrait
        );

        successMessage.value = `Successfully uploaded: ${result.filename} (ID: ${result.content_id})`;
        selectedFile.value = null;
        if (fileInput.value) {
          fileInput.value.value = '';
        }
        emit('uploadComplete');
      } catch (err) {
        error.value = 'Failed to upload artwork: ' + (err.response?.data?.detail || err.message);
        console.error(err);
      } finally {
        uploading.value = false;
      }
    };

    return {
      selectedFile,
      matte,
      uploading,
      successMessage,
      error,
      fileInput,
      handleFileSelect,
      handleUpload,
      formatFileSize,
    };
  },
};
</script>
