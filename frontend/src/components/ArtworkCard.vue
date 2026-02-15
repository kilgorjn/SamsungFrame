<template>
  <div class="art-card" :style="{ border: isCurrentArtwork ? '3px solid #28a745' : '', opacity: disabled ? 0.5 : 1 }">
    <div @click="handleClick" style="position: relative;" :style="{ cursor: disabled ? 'not-allowed' : 'pointer', pointerEvents: disabled ? 'none' : 'auto' }">
      <input
        v-if="selectionMode && !isCurrentArtwork"
        type="checkbox"
        :checked="isSelected"
        @click.stop="$emit('toggle-select', artwork.content_id)"
        style="position: absolute; top: 8px; left: 8px; width: 24px; height: 24px; cursor: pointer; z-index: 10;"
      />
      <div
        v-if="selectionMode && isCurrentArtwork"
        style="position: absolute; top: 8px; left: 8px; background: rgba(40, 167, 69, 0.9); color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; z-index: 10;"
      >
        Current
      </div>
      <div
        v-if="isSelecting"
        style="position: absolute; inset: 0; background: rgba(0, 0, 0, 0.6); display: flex; align-items: center; justify-content: center; z-index: 20;"
      >
        <div style="color: white; font-size: 14px; font-weight: bold;">
          Selecting...
        </div>
      </div>
      <img
        v-if="thumbnailUrl"
        :src="thumbnailUrl"
        :alt="artwork.content_id"
      />
      <div v-else style="width: 100%; height: 150px; max-height: 300px; background: #f5f5f5; display: flex; align-items: center; justify-content: center; color: #999;">
        <span v-if="loading">Loading...</span>
        <span v-else>{{ ['artstore', 'server', 'ambient'].includes(artwork.content_type) ? 'Art Store' : 'No preview' }}</span>
      </div>
    </div>
    <div class="art-card-content">
      <div class="art-card-title">
        {{ artwork.file_name || artwork.content_id }}
        <span v-if="isCurrentArtwork" style="color: #28a745; font-weight: bold; margin-left: 4px;">★</span>
      </div>
      <div v-if="artwork.file_name" style="font-size: 11px; color: #666; margin-top: 2px; font-family: monospace;">
        {{ artwork.content_id }}
      </div>
      <div v-if="artwork.width && artwork.height" style="font-size: 11px; color: #888; margin-top: 2px;">
        {{ artwork.width }} × {{ artwork.height }}
      </div>
      <div class="art-card-type">
        <span :class="['badge', ['artstore', 'server', 'ambient'].includes(artwork.content_type) ? 'badge-artstore' : 'badge-mobile']">
          {{
            artwork.content_type === 'ambient' ? 'Ambient' :
            ['artstore', 'server'].includes(artwork.content_type) ? 'Art Store' :
            'Uploaded'
          }}
        </span>
      </div>
      <button
        v-if="!selectionMode"
        @click="$emit('select', artwork.content_id)"
        :disabled="disabled || isSelecting"
        style="width: 100%; margin-top: 8px;"
      >
        {{ isSelecting ? 'Selecting...' : 'Select' }}
      </button>
      <button
        v-if="!selectionMode && !isCurrentArtwork"
        @click="handleDelete"
        style="width: 100%; margin-top: 4px; background-color: #dc3545; color: white;"
      >
        Delete
      </button>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { samsungApi } from '../api/samsung-api';

export default {
  name: 'ArtworkCard',
  props: {
    artwork: {
      type: Object,
      required: true,
    },
    currentArtworkId: {
      type: String,
      default: null,
    },
    selectionMode: {
      type: Boolean,
      default: false,
    },
    isSelected: {
      type: Boolean,
      default: false,
    },
    isSelecting: {
      type: Boolean,
      default: false,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['select', 'delete', 'toggle-select'],
  setup(props, { emit }) {
    const thumbnailUrl = ref(null);
    const loading = ref(false);

    const isCurrentArtwork = computed(() => {
      return props.currentArtworkId === props.artwork.content_id;
    });

    onMounted(async () => {
      // Only try to load thumbnails for user-uploaded content (mobile)
      // Skip Art Store content (artstore/server) as it's DRM-protected
      if (props.artwork.content_type === 'mobile') {
        loading.value = true;
        try {
          thumbnailUrl.value = await samsungApi.getThumbnail(props.artwork.content_id);
        } catch (err) {
          console.log('Could not load thumbnail:', err);
        } finally {
          loading.value = false;
        }
      }
    });

    const handleDelete = () => {
      const fileName = props.artwork.file_name || props.artwork.content_id;
      if (confirm(`Are you sure you want to delete "${fileName}"? This cannot be undone.`)) {
        emit('delete', props.artwork.content_id);
      }
    };

    const handleClick = () => {
      if (props.disabled) return;

      if (props.selectionMode) {
        // Don't allow selecting the current artwork
        if (!isCurrentArtwork.value) {
          emit('toggle-select', props.artwork.content_id);
        }
      } else {
        emit('select', props.artwork.content_id);
      }
    };

    return { thumbnailUrl, loading, isCurrentArtwork, handleDelete, handleClick };
  },
};
</script>
