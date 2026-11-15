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
      <div style="margin-top: 16px;">
        <button @click="showOnTv" :disabled="showing" style="width: 100%; max-width: 400px;">
          {{ showing ? 'Showing on TV...' : '📺 Show on TV' }}
        </button>
        <p v-if="showMessage" class="success" style="margin-top: 8px;">{{ showMessage }}</p>
      </div>

      <!-- Brightness Control -->
      <div style="margin-top: 24px; padding-top: 24px; border-top: 1px solid #e0e0e0;">
        <h3 style="margin-bottom: 16px;">Brightness</h3>
        <div style="display: flex; align-items: center; gap: 16px; max-width: 400px;">
          <span style="font-size: 20px;">🌙</span>
          <input
            type="range"
            v-model="brightness"
            @input="onBrightnessChange"
            :disabled="autoBrightness"
            min="0"
            max="10"
            step="1"
            style="flex: 1; height: 6px; cursor: pointer;"
          />
          <span style="font-size: 20px;">☀️</span>
          <span style="min-width: 30px; text-align: center; font-weight: 600;">{{ brightness }}</span>
        </div>
        <label style="display: flex; align-items: center; gap: 8px; margin-top: 12px; cursor: pointer;">
          <input type="checkbox" v-model="autoBrightness" @change="onAutoBrightnessChange" />
          Auto brightness (use the TV's light sensor)
        </label>
        <p v-if="brightnessMessage" class="success" style="margin-top: 8px;">{{ brightnessMessage }}</p>
        <p v-if="brightnessError" class="error" style="margin-top: 8px;">{{ brightnessError }}</p>
      </div>

      <!-- Color Temperature Control -->
      <div style="margin-top: 24px; padding-top: 24px; border-top: 1px solid #e0e0e0;">
        <h3 style="margin-bottom: 16px;">Color Temperature</h3>
        <div style="display: flex; align-items: center; gap: 16px; max-width: 400px;">
          <span style="font-size: 20px;">❄️</span>
          <input
            type="range"
            v-model="colorTemp"
            @input="onColorTempChange"
            min="-5"
            max="5"
            step="1"
            style="flex: 1; height: 6px; cursor: pointer;"
          />
          <span style="font-size: 20px;">🔥</span>
          <span style="min-width: 30px; text-align: center; font-weight: 600;">{{ colorTemp }}</span>
        </div>
        <p v-if="colorTempMessage" class="success" style="margin-top: 8px;">{{ colorTempMessage }}</p>
        <p v-if="colorTempError" class="error" style="margin-top: 8px;">{{ colorTempError }}</p>
      </div>

      <!-- Matte Picker -->
      <div v-if="currentArt && matteTypes && matteColors" style="margin-top: 24px; padding-top: 24px; border-top: 1px solid #e0e0e0;">
        <h3
          @click="matteExpanded = !matteExpanded"
          style="margin-bottom: 16px; cursor: pointer; user-select: none; display: flex; align-items: center; gap: 8px;"
        >
          <span>{{ matteExpanded ? '▼' : '▶' }}</span>
          Matte Style
        </h3>

        <div v-if="matteExpanded">
          <div style="margin-bottom: 16px;">
            <label style="display: block; margin-bottom: 8px;"><strong>Type:</strong></label>
          <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(100px, 1fr)); gap: 8px;">
            <button
              v-for="type in matteTypes"
              :key="type.matte_type"
              @click="selectMatteType(type.matte_type)"
              :style="{
                padding: '8px',
                fontSize: '12px',
                background: selectedType === type.matte_type ? '#0066cc' : '#f5f5f5',
                color: selectedType === type.matte_type ? 'white' : '#333',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }"
            >
              {{ type.matte_type }}
            </button>
            </div>
          </div>

          <div style="margin-bottom: 16px;">
            <label style="display: block; margin-bottom: 8px;"><strong>Color:</strong></label>
            <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(90px, 1fr)); gap: 8px;">
              <button
                v-for="color in matteColors"
                :key="color.color"
                @click="selectMatteColor(color.color)"
                :style="{
                  padding: '8px',
                  fontSize: '11px',
                  background: selectedColor === color.color ? '#0066cc' : '#f5f5f5',
                  color: selectedColor === color.color ? 'white' : '#333',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px'
                }"
              >
                <span :style="{
                  display: 'inline-block',
                  width: '16px',
                  height: '16px',
                  borderRadius: '50%',
                  backgroundColor: `rgb(${color.R}, ${color.G}, ${color.B})`,
                  border: '1px solid #ddd'
                }"></span>
                {{ color.color }}
              </button>
            </div>
          </div>

          <button
            @click="applyMatte"
            :disabled="changingMatte || !selectedType || !selectedColor"
            style="width: 100%; max-width: 400px; background-color: #28a745;"
          >
            {{ changingMatte ? 'Applying...' : 'Apply Matte' }}
          </button>
          <p v-if="matteMessage" class="success" style="margin-top: 8px;">{{ matteMessage }}</p>
          <p v-if="matteError" class="error" style="margin-top: 8px;">{{ matteError }}</p>
        </div>
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
    const showing = ref(false);
    const showMessage = ref(null);

    // Matte picker state
    const matteExpanded = ref(false);
    const matteTypes = ref(null);
    const matteColors = ref(null);
    const selectedType = ref(null);
    const selectedColor = ref(null);
    const changingMatte = ref(false);
    const matteMessage = ref(null);
    const matteError = ref(null);

    // Brightness state
    const brightness = ref(5);
    const brightnessMessage = ref(null);
    const brightnessError = ref(null);
    const autoBrightness = ref(false);
    let brightnessTimeout = null;

    // Color temperature state
    const colorTemp = ref(0);
    const colorTempMessage = ref(null);
    const colorTempError = ref(null);
    let colorTempTimeout = null;

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

    const showOnTv = async () => {
      if (!currentArt.value) return;

      showing.value = true;
      showMessage.value = null;

      try {
        await samsungApi.selectArtwork(currentArt.value.content_id, currentArt.value.category_id, true);
        showMessage.value = 'Artwork displayed on TV!';
        setTimeout(() => {
          showMessage.value = null;
        }, 3000);
      } catch (err) {
        error.value = 'Failed to show artwork on TV';
        console.error(err);
      } finally {
        showing.value = false;
      }
    };

    const loadMatteList = async () => {
      try {
        const data = await samsungApi.getMatteList();
        matteTypes.value = data.matte_types;
        matteColors.value = data.matte_colors;

        // Parse current matte if available
        if (currentArt.value && currentArt.value.matte_id) {
          const parts = currentArt.value.matte_id.split('_');
          if (parts.length === 2) {
            selectedType.value = parts[0];
            selectedColor.value = parts[1];
          }
        }
      } catch (err) {
        console.error('Failed to load matte list:', err);
      }
    };

    const selectMatteType = (type) => {
      selectedType.value = type;
      matteError.value = null;
    };

    const selectMatteColor = (color) => {
      selectedColor.value = color;
      matteError.value = null;
    };

    const applyMatte = async () => {
      if (!currentArt.value || !selectedType.value || !selectedColor.value) return;

      changingMatte.value = true;
      matteMessage.value = null;
      matteError.value = null;

      try {
        const matteId = `${selectedType.value}_${selectedColor.value}`;
        await samsungApi.changeMatte(currentArt.value.content_id, matteId);

        // Show the artwork with the new matte on TV immediately
        await samsungApi.selectArtwork(currentArt.value.content_id, currentArt.value.category_id, true);

        matteMessage.value = 'Matte updated and displayed on TV!';
        currentArt.value.matte_id = matteId;

        setTimeout(() => {
          matteMessage.value = null;
        }, 3000);
      } catch (err) {
        matteError.value = 'Failed to change matte. Some mattes may not be compatible with this image size.';
        console.error(err);
      } finally {
        changingMatte.value = false;
      }
    };

    const loadTvSettings = async () => {
      try {
        const settings = await samsungApi.getTvSettings();
        if (settings.color_temperature) {
          colorTemp.value = parseInt(settings.color_temperature);
        }
        if (settings.brightness) {
          brightness.value = parseInt(settings.brightness);
        }
        if (typeof settings.auto_brightness === 'boolean') {
          autoBrightness.value = settings.auto_brightness;
        }
      } catch (err) {
        console.error('Failed to load TV settings:', err);
      }
    };

    const onAutoBrightnessChange = async () => {
      const enabled = autoBrightness.value;
      brightnessMessage.value = null;
      brightnessError.value = null;
      try {
        await samsungApi.setAutoBrightness(enabled);
        brightnessMessage.value = `Auto brightness ${enabled ? 'on' : 'off'}`;
        setTimeout(() => {
          brightnessMessage.value = null;
        }, 2000);
      } catch (err) {
        autoBrightness.value = !enabled;
        brightnessError.value = 'Failed to change auto brightness';
        console.error(err);
      }
    };

    const onBrightnessChange = () => {
      // Clear any existing timeout
      if (brightnessTimeout) {
        clearTimeout(brightnessTimeout);
      }

      brightnessMessage.value = null;
      brightnessError.value = null;

      // Debounce: wait 500ms after user stops dragging before sending request
      brightnessTimeout = setTimeout(async () => {
        try {
          await samsungApi.setBrightness(brightness.value);
          brightnessMessage.value = `Brightness set to ${brightness.value}`;
          setTimeout(() => {
            brightnessMessage.value = null;
          }, 2000);
        } catch (err) {
          brightnessError.value = 'Failed to set brightness';
          console.error(err);
        }
      }, 500);
    };

    const onColorTempChange = () => {
      // Clear any existing timeout
      if (colorTempTimeout) {
        clearTimeout(colorTempTimeout);
      }

      colorTempMessage.value = null;
      colorTempError.value = null;

      // Debounce: wait 500ms after user stops dragging before sending request
      colorTempTimeout = setTimeout(async () => {
        try {
          await samsungApi.setColorTemperature(colorTemp.value);
          colorTempMessage.value = `Color temperature set to ${colorTemp.value}`;
          setTimeout(() => {
            colorTempMessage.value = null;
          }, 2000);
        } catch (err) {
          colorTempError.value = 'Failed to set color temperature';
          console.error(err);
        }
      }, 500);
    };

    onMounted(async () => {
      // Run in parallel; the TV handles each request in roughly a second
      await Promise.all([
        loadCurrentArtwork().then(loadMatteList),
        loadTvSettings(),
      ]);
    });

    return {
      currentArt,
      thumbnailUrl,
      error,
      showing,
      showMessage,
      showOnTv,
      brightness,
      brightnessMessage,
      brightnessError,
      onBrightnessChange,
      autoBrightness,
      onAutoBrightnessChange,
      colorTemp,
      colorTempMessage,
      colorTempError,
      onColorTempChange,
      matteExpanded,
      matteTypes,
      matteColors,
      selectedType,
      selectedColor,
      changingMatte,
      matteMessage,
      matteError,
      selectMatteType,
      selectMatteColor,
      applyMatte,
      refresh: loadCurrentArtwork,
    };
  },
};
</script>

<style scoped>
</style>
