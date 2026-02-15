<template>
  <div class="container">
    <h2>Art Gallery</h2>

    <div v-if="artworks" style="margin-bottom: 16px; display: flex; gap: 12px; align-items: center; flex-wrap: wrap;">
      <div>
        <label style="margin-right: 8px;">
          <strong>Filter:</strong>
        </label>
        <select v-model="filter" style="min-width: 150px;">
          <option value="all">All ({{ artworks.length }})</option>
          <option value="mobile">Uploaded Only ({{ uploadedCount }})</option>
          <option value="artstore">Art Store Only ({{ artstoreCount }})</option>
        </select>
      </div>

      <button
        v-if="!selectionMode"
        @click="enableSelectionMode"
        style="background-color: #6c757d; color: white;"
      >
        Select Multiple
      </button>

      <div v-if="selectionMode" style="display: flex; gap: 8px;">
        <button
          @click="deleteSelected"
          :disabled="selectedIds.length === 0"
          style="background-color: #dc3545; color: white;"
        >
          Delete Selected ({{ selectedIds.length }})
        </button>
        <button @click="cancelSelection">Cancel</button>
      </div>
    </div>

    <div v-if="filteredArtworks && filteredArtworks.length > 0" class="art-grid">
      <ArtworkCard
        v-for="artwork in filteredArtworks"
        :key="artwork.content_id"
        :artwork="artwork"
        :current-artwork-id="currentArtworkId"
        :selection-mode="selectionMode"
        :is-selected="selectedIds.includes(artwork.content_id)"
        :is-selecting="selectingArtworkId === artwork.content_id"
        :disabled="selectingArtworkId !== null && selectingArtworkId !== artwork.content_id"
        @select="handleSelect"
        @delete="handleDelete"
        @toggle-select="toggleSelect"
      />
    </div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="loading" class="loading">Loading artwork gallery...</div>
    <div v-else class="loading">No artwork found</div>

    <div v-if="successMessage" class="success">{{ successMessage }}</div>
    <div v-if="selectError" class="error">{{ selectError }}</div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { samsungApi } from '../api/samsung-api';
import ArtworkCard from './ArtworkCard.vue';

export default {
  name: 'ArtGallery',
  components: {
    ArtworkCard,
  },
  emits: ['artworkSelected'],
  setup(props, { emit }) {
    const artworks = ref(null);
    const currentArtworkId = ref(null);
    const filter = ref('all');
    const loading = ref(false);
    const error = ref(null);
    const successMessage = ref(null);
    const selectError = ref(null);
    const selectionMode = ref(false);
    const selectedIds = ref([]);
    const selectingArtworkId = ref(null);

    const filteredArtworks = computed(() => {
      if (!artworks.value) return [];
      if (filter.value === 'all') return artworks.value;
      return artworks.value.filter(art => art.content_type === filter.value);
    });

    const uploadedCount = computed(() => {
      return artworks.value?.filter(art => art.content_type === 'mobile').length || 0;
    });

    const artstoreCount = computed(() => {
      return artworks.value?.filter(art =>
        art.content_type === 'artstore' ||
        art.content_type === 'server' ||
        art.content_type === 'ambient'
      ).length || 0;
    });

    const loadCurrentArtwork = async () => {
      try {
        const current = await samsungApi.getCurrentArtwork();
        currentArtworkId.value = current.content_id;
      } catch (err) {
        console.error('Failed to load current artwork:', err);
      }
    };

    const loadArtworks = async () => {
      loading.value = true;
      error.value = null;
      try {
        const response = await samsungApi.getArtworkList();
        artworks.value = response.artworks;
        await loadCurrentArtwork();
      } catch (err) {
        error.value = 'Failed to load artwork gallery';
        console.error(err);
      } finally {
        loading.value = false;
      }
    };

    const handleSelect = async (contentId) => {
      // Prevent selecting while another selection is in progress
      if (selectingArtworkId.value) return;

      successMessage.value = null;
      selectError.value = null;
      selectingArtworkId.value = contentId;

      try {
        await samsungApi.selectArtwork(contentId);
        successMessage.value = `Successfully selected artwork: ${contentId}`;
        currentArtworkId.value = contentId;
        emit('artworkSelected');
      } catch (err) {
        selectError.value = 'Failed to select artwork';
        console.error(err);
      } finally {
        selectingArtworkId.value = null;
      }
    };

    const handleDelete = async (contentId) => {
      successMessage.value = null;
      selectError.value = null;
      try {
        await samsungApi.deleteArtwork(contentId);
        successMessage.value = `Successfully deleted artwork: ${contentId}`;
        // Refresh the gallery to show updated list
        await loadArtworks();
      } catch (err) {
        // Show specific error message from backend if available
        selectError.value = err.response?.data?.detail || 'Failed to delete artwork';
        console.error(err);
      }
    };

    const enableSelectionMode = () => {
      selectionMode.value = true;
      selectedIds.value = [];
    };

    const cancelSelection = () => {
      selectionMode.value = false;
      selectedIds.value = [];
    };

    const toggleSelect = (contentId) => {
      // Don't allow selecting the current artwork
      if (contentId === currentArtworkId.value) {
        return;
      }

      const index = selectedIds.value.indexOf(contentId);
      if (index === -1) {
        selectedIds.value.push(contentId);
      } else {
        selectedIds.value.splice(index, 1);
      }
    };

    const deleteSelected = async () => {
      if (selectedIds.value.length === 0) return;

      const count = selectedIds.value.length;
      if (!confirm(`Are you sure you want to delete ${count} artwork(s)? This cannot be undone.`)) {
        return;
      }

      successMessage.value = null;
      selectError.value = null;

      let successCount = 0;
      let failedCount = 0;
      const errors = [];

      for (const contentId of selectedIds.value) {
        try {
          await samsungApi.deleteArtwork(contentId);
          successCount++;
        } catch (err) {
          failedCount++;
          const errorMsg = err.response?.data?.detail || 'Unknown error';
          errors.push(`${contentId}: ${errorMsg}`);
        }
      }

      // Exit selection mode
      selectionMode.value = false;
      selectedIds.value = [];

      // Refresh gallery
      await loadArtworks();

      // Show results
      if (successCount > 0) {
        successMessage.value = `Successfully deleted ${successCount} artwork(s)`;
      }
      if (failedCount > 0) {
        selectError.value = `Failed to delete ${failedCount} artwork(s): ${errors.join('; ')}`;
      }
    };

    onMounted(loadArtworks);

    return {
      artworks,
      currentArtworkId,
      filter,
      filteredArtworks,
      uploadedCount,
      artstoreCount,
      loading,
      error,
      successMessage,
      selectError,
      selectionMode,
      selectedIds,
      selectingArtworkId,
      handleSelect,
      handleDelete,
      enableSelectionMode,
      cancelSelection,
      toggleSelect,
      deleteSelected,
      refresh: loadArtworks,
    };
  },
};
</script>
