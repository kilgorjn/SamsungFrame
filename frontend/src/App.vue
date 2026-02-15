<template>
  <div id="app">
    <header style="text-align: center; margin-bottom: 32px;">
      <h1 style="font-size: 32px; margin-bottom: 8px;">🖼️ Samsung Frame Art Controller</h1>
      <p style="color: #666;">Manage your Samsung Frame TV artwork</p>
    </header>

    <TvStatus ref="tvStatus" />

    <CurrentArtwork ref="currentArtwork" />

    <UploadForm @uploadComplete="handleUploadComplete" />

    <ArtGallery ref="gallery" @artworkSelected="handleArtworkSelected" />

    <footer style="text-align: center; margin-top: 48px; padding: 24px; color: #999; font-size: 14px;">
      <p>Samsung Frame Art Controller v1.0</p>
    </footer>
  </div>
</template>

<script>
import { ref } from 'vue';
import TvStatus from './components/TvStatus.vue';
import CurrentArtwork from './components/CurrentArtwork.vue';
import ArtGallery from './components/ArtGallery.vue';
import UploadForm from './components/UploadForm.vue';

export default {
  name: 'App',
  components: {
    TvStatus,
    CurrentArtwork,
    ArtGallery,
    UploadForm,
  },
  setup() {
    const currentArtwork = ref(null);
    const gallery = ref(null);

    const handleUploadComplete = () => {
      // Refresh gallery after upload
      if (gallery.value) {
        gallery.value.refresh();
      }
    };

    const handleArtworkSelected = () => {
      // Refresh current artwork display after selection
      if (currentArtwork.value) {
        setTimeout(() => {
          currentArtwork.value.refresh();
        }, 1000); // Small delay to let TV update
      }
    };

    return {
      currentArtwork,
      gallery,
      handleUploadComplete,
      handleArtworkSelected,
    };
  },
};
</script>
