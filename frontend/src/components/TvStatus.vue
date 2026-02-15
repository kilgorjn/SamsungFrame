<template>
  <div class="container">
    <h2>TV Status</h2>
    <div v-if="status">
      <p>
        <span :class="['status-indicator', status.power_on ? 'status-online' : 'status-offline']"></span>
        <strong>Power:</strong> {{ status.power_on ? 'On' : 'Off' }}
      </p>
      <p>
        <span :class="['status-indicator', status.tv_reachable ? 'status-online' : 'status-offline']"></span>
        <strong>Connection:</strong> {{ status.tv_reachable ? 'Connected' : 'Disconnected' }}
      </p>
      <p v-if="status.art_mode_supported !== undefined">
        <strong>Art Mode Supported:</strong> {{ status.art_mode_supported ? 'Yes' : 'No' }}
      </p>
      <p v-if="status.art_mode_active !== null && status.art_mode_active !== undefined">
        <strong>Art Mode Active:</strong> {{ status.art_mode_active ? 'Yes' : 'No' }}
      </p>
      <p v-if="status.api_version">
        <strong>API Version:</strong> {{ status.api_version }}
      </p>
      <p>
        <strong>Optimal Dimensions:</strong> 3840 × 2160 (16:9)
      </p>
    </div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="loading">Loading TV status...</div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { samsungApi } from '../api/samsung-api';

export default {
  name: 'TvStatus',
  setup() {
    const status = ref(null);
    const error = ref(null);

    const loadStatus = async () => {
      try {
        status.value = await samsungApi.getTvStatus();
        error.value = null;
      } catch (err) {
        error.value = 'Failed to load TV status';
        console.error(err);
      }
    };

    onMounted(loadStatus);

    return { status, error };
  },
};
</script>
