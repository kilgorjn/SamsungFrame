<template>
  <div class="container">
    <h2>Current Artwork</h2>
    <div v-if="currentArt">
      <div style="margin-bottom: 16px;">
        <div style="max-width: 400px; margin: 0 auto;">
          <img
            v-if="thumbnailUrl"
            :src="thumbnailUrl"
            :alt="currentArt.content_id"
            style="width: 100%; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);"
          />
          <div v-else style="background: #f5f5f5; padding: 60px; text-align: center; border-radius: 8px;">
            <p style="color: #666;">
              {{ currentArt.content_type === 'artstore' ? 'Art Store content (preview not available)' : 'Loading preview...' }}
            </p>
          </div>
        </div>
      </div>
      <div>
        <p><strong>ID:</strong> {{ currentArt.content_id }}</p>
        <p>
          <strong>Type:</strong>
          <span :class="['badge', currentArt.content_type === 'artstore' ? 'badge-artstore' : 'badge-mobile']">
            {{ currentArt.content_type === 'artstore' ? 'Art Store' : 'Uploaded' }}
          </span>
        </p>
        <p v-if="currentArt.matte_id"><strong>Matte:</strong> {{ currentArt.matte_id }}</p>
        <p v-if="currentArt.category_id"><strong>Category:</strong> {{ currentArt.category_id }}</p>
      </div>
    </div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="loading">Loading current artwork...</div>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue';
import { samsungApi } from '../api/samsung-api';

export default {
  name: 'CurrentArtwork',
  setup() {
    const currentArt = ref(null);
    const thumbnailUrl = ref(null);
    const error = ref(null);

    const loadCurrentArtwork = async () => {
      try {
        currentArt.value = await samsungApi.getCurrentArtwork();
        error.value = null;

        // Try to load thumbnail
        if (currentArt.value) {
          try {
            thumbnailUrl.value = await samsungApi.getThumbnail(currentArt.value.content_id);
          } catch (err) {
            console.log('Thumbnail not available:', err);
          }
        }
      } catch (err) {
        error.value = 'Failed to load current artwork';
        console.error(err);
      }
    };

    onMounted(loadCurrentArtwork);

    return {
      currentArt,
      thumbnailUrl,
      error,
      refresh: loadCurrentArtwork,
    };
  },
};
</script>
