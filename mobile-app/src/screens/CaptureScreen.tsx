import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, ScrollView, StyleSheet, Image, Alert } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { useAudioRecorder, RecordingPresets, AudioModule, setAudioModeAsync } from 'expo-audio';
import { C } from '../lib/theme';
import { Observation, ObservationType, Discipline, Settings } from '../lib/types';

const TYPES: ObservationType[] = ['START', 'PROGRESS', 'FINISH', 'HOLD', 'QA_CLEARANCE', 'INSPECTION'];
const DISCIPLINES: Discipline[] = ['CIVIL', 'PIPING', 'STRUCTURAL', 'MECHANICAL', 'ELECTRICAL', 'INSTRUMENTATION', 'QA_QC', 'SAFETY_HSE'];
const UNITS = ['Meters', 'Joints', 'Spools', 'Cu.M', 'Sq.M', 'MT', 'Nos', 'Loops', '%'];

interface Props { settings: Settings; onSave: (o: Observation) => void; }

export function CaptureScreen({ settings, onSave }: Props) {
  const [type, setType] = useState<ObservationType>('PROGRESS');
  const [discipline, setDiscipline] = useState<Discipline>('CIVIL');
  const [activityId, setActivityId] = useState('');
  const [location, setLocation] = useState('');
  const [quantity, setQuantity] = useState('');
  const [unit, setUnit] = useState('Meters');
  const [statement, setStatement] = useState('');
  const [photoUri, setPhotoUri] = useState<string | undefined>();
  const [audioUri, setAudioUri] = useState<string | undefined>();
  const recorder = useAudioRecorder(RecordingPresets.HIGH_QUALITY);
  const [recording, setRecording] = useState(false);

  async function takePhoto() {
    const perm = await ImagePicker.requestCameraPermissionsAsync();
    if (!perm.granted) { Alert.alert('Camera permission denied'); return; }
    const res = await ImagePicker.launchCameraAsync({ quality: 0.5 });
    if (!res.canceled && res.assets[0]) setPhotoUri(res.assets[0].uri);
  }

  async function toggleRecord() {
    if (recording) {
      await recorder.stop();
      setRecording(false);
      setAudioUri(recorder.uri ?? undefined);
      return;
    }
    const perm = await AudioModule.requestRecordingPermissionsAsync();
    if (!perm.granted) { Alert.alert('Microphone permission denied'); return; }
    await setAudioModeAsync({ allowsRecording: true, playsInSilentMode: true });
    await recorder.prepareToRecordAsync();
    recorder.record();
    setRecording(true);
  }

  function save() {
    if (!statement.trim() && !audioUri) {
      Alert.alert('Add a description', 'Write what happened on site, or record a voice note.');
      return;
    }
    const now = new Date();
    const obs: Observation = {
      id: `OBS-${now.getTime().toString(36).toUpperCase()}`,
      projectId: settings.projectId,
      activityId: activityId.trim() || undefined,
      type, discipline,
      location: location.trim(),
      quantity: quantity.trim() || undefined,
      unit: quantity.trim() ? unit : undefined,
      statement: statement.trim() || 'Voice observation recorded',
      photoUri, audioUri,
      observedAt: now.toISOString().slice(0, 10),
      createdAt: now.toISOString(),
      syncStatus: 'PENDING',
    };
    onSave(obs);
    setActivityId(''); setLocation(''); setQuantity(''); setStatement('');
    setPhotoUri(undefined); setAudioUri(undefined);
    Alert.alert('Saved offline', 'Observation queued. Sync when you have network.');
  }

  return (
    <ScrollView style={s.root} contentContainerStyle={{ padding: 16, paddingBottom: 48 }} keyboardShouldPersistTaps="handled">
      <Text style={s.h1}>Log Observation</Text>
      <Text style={s.sub}>Project {settings.projectId} · {new Date().toDateString()}</Text>

      <Text style={s.label}>Event type</Text>
      <Chips options={TYPES} value={type} onChange={setType} />

      <Text style={s.label}>Discipline</Text>
      <Chips options={DISCIPLINES} value={discipline} onChange={setDiscipline} />

      <Text style={s.label}>Activity ID (optional, e.g. ACT-1010)</Text>
      <TextInput style={s.input} value={activityId} onChangeText={setActivityId} autoCapitalize="characters" placeholder="ACT-1010" placeholderTextColor={C.muted} />

      <Text style={s.label}>Location / chainage</Text>
      <TextInput style={s.input} value={location} onChangeText={setLocation} placeholder="Section 1, Km 0.0 to 2.0" placeholderTextColor={C.muted} />

      <Text style={s.label}>Quantity</Text>
      <TextInput style={s.input} value={quantity} onChangeText={setQuantity} keyboardType="numeric" placeholder="500" placeholderTextColor={C.muted} />
      <View style={{ height: 8 }} />
      <Chips options={UNITS} value={unit} onChange={setUnit} />

      <Text style={s.label}>What happened</Text>
      <TextInput style={[s.input, { height: 100, textAlignVertical: 'top' }]} multiline value={statement} onChangeText={setStatement}
        placeholder="Mainline ROW clearing and grading completed today, NDT clearance pending." placeholderTextColor={C.muted} />

      <View style={{ flexDirection: 'row', gap: 10, marginTop: 14 }}>
        <TouchableOpacity style={[s.btn, s.btnAlt]} onPress={takePhoto}>
          <Text style={s.btnAltText}>{photoUri ? 'Retake photo' : 'Capture photo'}</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[s.btn, s.btnAlt, recording && { borderColor: C.red }]} onPress={toggleRecord}>
          <Text style={[s.btnAltText, recording && { color: C.red }]}>{recording ? 'Stop recording' : audioUri ? 'Re-record voice' : 'Voice note'}</Text>
        </TouchableOpacity>
      </View>
      {photoUri && <Image source={{ uri: photoUri }} style={s.preview} />}
      {audioUri && !recording && <Text style={s.hint}>Voice note attached</Text>}

      <TouchableOpacity style={[s.btn, s.btnPrimary]} onPress={save}>
        <Text style={s.btnPrimaryText}>Save to sync queue</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

function Chips<T extends string>({ options, value, onChange }: { options: T[]; value: T; onChange: (v: T) => void }) {
  return (
    <View style={s.chips}>
      {options.map(o => (
        <TouchableOpacity key={o} onPress={() => onChange(o)} style={[s.chip, o === value && s.chipOn]}>
          <Text style={[s.chipText, o === value && s.chipTextOn]}>{o.replace('_', ' ')}</Text>
        </TouchableOpacity>
      ))}
    </View>
  );
}

const s = StyleSheet.create({
  root: { flex: 1, backgroundColor: C.bg },
  h1: { color: C.text, fontSize: 22, fontWeight: '700', letterSpacing: 1 },
  sub: { color: C.muted, fontSize: 12, marginBottom: 12 },
  label: { color: C.muted, fontSize: 12, marginTop: 14, marginBottom: 6, textTransform: 'uppercase', letterSpacing: 1 },
  input: { backgroundColor: C.card, borderColor: C.border, borderWidth: 1, borderRadius: 8, color: C.text, padding: 12, fontSize: 15 },
  chips: { flexDirection: 'row', flexWrap: 'wrap', gap: 6 },
  chip: { paddingHorizontal: 12, paddingVertical: 7, borderRadius: 16, borderWidth: 1, borderColor: C.border, backgroundColor: C.card },
  chipOn: { backgroundColor: C.accent, borderColor: C.accent },
  chipText: { color: C.muted, fontSize: 12 },
  chipTextOn: { color: '#000', fontWeight: '700' },
  btn: { flex: 1, padding: 14, borderRadius: 8, alignItems: 'center' },
  btnAlt: { borderWidth: 1, borderColor: C.border, backgroundColor: C.card },
  btnAltText: { color: C.text, fontWeight: '600' },
  btnPrimary: { backgroundColor: C.accent, marginTop: 20 },
  btnPrimaryText: { color: '#000', fontWeight: '800', fontSize: 16 },
  preview: { width: '100%', height: 180, borderRadius: 8, marginTop: 12 },
  hint: { color: C.green, marginTop: 8, fontSize: 12 },
});
