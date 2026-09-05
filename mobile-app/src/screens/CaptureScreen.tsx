import React, { useMemo, useState } from 'react';
import { View, Text, ScrollView, TouchableOpacity, StyleSheet, Image, Alert, Modal, FlatList, TextInput, KeyboardAvoidingView, Platform } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { useAudioRecorder, RecordingPresets, AudioModule, setAudioModeAsync } from 'expo-audio';
import { Screen, Header, Icon, IconButton, Label, Mono, Button, Segmented, Card, Input } from '../components/ui';
import { C } from '../lib/theme';
import { Activity, Observation, ObservationType, Settings, DISCIPLINES, UNITS, AuditActivity } from '../lib/types';

interface Props {
  settings: Settings; activities: Activity[]; initialActivity: Activity | null; claim?: AuditActivity | null;
  onSubmit: (o: Observation, draft: boolean) => void; onBack: () => void;
}

export function CaptureScreen({ settings, activities, initialActivity, claim, onSubmit, onBack }: Props) {
  const isAudit = settings.role === 'MANAGER';
  const [activity, setActivity] = useState<Activity | null>(initialActivity);
  const [type, setType] = useState<ObservationType>('PROGRESS');
  const [note, setNote] = useState('');
  const [discipline, setDiscipline] = useState(initialActivity?.discipline || 'CIVIL');
  const [area, setArea] = useState(initialActivity?.area_location || '');
  const [quantity, setQuantity] = useState('');
  const [unit, setUnit] = useState(initialActivity?.unit_of_measure || 'Meters');
  const [when] = useState(new Date());
  const [photoUri, setPhotoUri] = useState<string>();
  const [audioUri, setAudioUri] = useState<string>();
  const [recording, setRecording] = useState(false);
  const [picker, setPicker] = useState(false);
  const [discPicker, setDiscPicker] = useState(false);
  const recorder = useAudioRecorder(RecordingPresets.HIGH_QUALITY);

  function chooseActivity(a: Activity | null) {
    setActivity(a);
    if (a) { setDiscipline(a.discipline); setArea(a.area_location || ''); if (a.unit_of_measure) setUnit(a.unit_of_measure); }
    setPicker(false);
  }

  async function takePhoto() {
    const p = await ImagePicker.requestCameraPermissionsAsync();
    if (!p.granted) return Alert.alert('Camera permission needed');
    const r = await ImagePicker.launchCameraAsync({ quality: 0.5 });
    if (!r.canceled && r.assets[0]) setPhotoUri(r.assets[0].uri);
  }
  async function toggleRecord() {
    if (recording) { await recorder.stop(); setRecording(false); setAudioUri(recorder.uri ?? undefined); return; }
    const p = await AudioModule.requestRecordingPermissionsAsync();
    if (!p.granted) return Alert.alert('Microphone permission needed');
    await setAudioModeAsync({ allowsRecording: true, playsInSilentMode: true });
    await recorder.prepareToRecordAsync(); recorder.record(); setRecording(true);
  }

  function build(draft: boolean) {
    if (!draft && !note.trim() && !audioUri && !activity) return Alert.alert('Add a field note', 'Describe what happened, pick an activity, or record a voice note.');
    onSubmit({
      id: `OBS-${Date.now().toString(36).toUpperCase()}`,
      projectId: settings.projectId,
      activityId: activity?.activity_id, activityName: activity?.activity_name,
      type, discipline, area: area.trim(), note: note.trim(),
      quantity: quantity.trim() || undefined, unit: quantity.trim() ? unit : undefined,
      photoUri, audioUri,
      observedAt: when.toISOString(), createdAt: new Date().toISOString(),
      syncStatus: draft ? 'DRAFT' : 'PENDING',
      isAudit, author: settings.name,
    }, draft);
  }

  const whenText = `${when.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }).toUpperCase()} · ${when.toTimeString().slice(0, 5)}`;

  return (
    <Screen>
      <Header title={isAudit ? 'RECORD AUDIT' : 'LOG OBSERVATION'} onBack={onBack} />
      <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
        <ScrollView contentContainerStyle={{ padding: 20, paddingBottom: 40 }} keyboardShouldPersistTaps="handled">

          <TouchableOpacity activeOpacity={0.85} onPress={() => setPicker(true)}>
            <Card accent={C.amber} style={{ marginBottom: 26, flexDirection: 'row', alignItems: 'center' }}>
              <View style={{ flex: 1 }}>
                {activity ? (<>
                  <Mono style={{ color: C.orange }}>{activity.activity_id}</Mono>
                  <Text style={s.actName}>{activity.activity_name}</Text>
                </>) : (<>
                  <Text style={{ color: C.text, fontSize: 16, fontWeight: '600' }}>Select schedule activity</Text>
                  <Text style={{ color: C.muted, fontSize: 13, marginTop: 4 }}>Optional. SATYA will match it if left blank.</Text>
                </>)}
              </View>
              {activity ? <IconButton name="x" color={C.muted} onPress={() => chooseActivity(null)} /> : <Icon name="chevron-right" color={C.muted} size={22} />}
            </Card>
          </TouchableOpacity>

          {isAudit && claim?.latest_claim && (
            <Card style={{ marginBottom: 22, backgroundColor: C.surface2 }}>
              <Label>WORKER CLAIMED</Label>
              <Text style={{ color: C.text, fontSize: 16, fontWeight: '600' }}>
                {claim.latest_claim.event_type === 'FINISH' ? 'Completed' : claim.latest_claim.event_type === 'HOLD' ? 'On hold' : 'In progress'}
                {claim.claimed_quantity != null ? ` · ${claim.claimed_quantity} ${claim.unit ?? ''}` : ''}
              </Text>
              <Mono style={{ marginTop: 4, fontSize: 12 }}>{claim.latest_claim.author} · {claim.latest_claim.observed_at?.slice(0, 10)} · {claim.worker_claim_count} report(s)</Mono>
              <Text style={{ color: C.muted, fontSize: 13, marginTop: 8, fontStyle: 'italic' }}>"{claim.latest_claim.statement}"</Text>
            </Card>
          )}
          <Label>{isAudit ? 'WHAT DID YOU FIND ON SITE?' : 'OBSERVATION TYPE'}</Label>
          <Segmented value={type} onChange={setType} options={isAudit
            ? [{ key: 'PROGRESS', label: 'In progress' }, { key: 'ISSUE', label: 'Problem' }, { key: 'COMPLETION', label: 'Verified done' }]
            : [{ key: 'PROGRESS', label: 'Progress Note' }, { key: 'ISSUE', label: 'Issue' }, { key: 'COMPLETION', label: 'Completion' }]} />

          <Label style={{ marginTop: 26 }}>{isAudit ? 'AUDIT NOTE' : 'FIELD NOTE'}</Label>
          <TextInput value={note} onChangeText={setNote} multiline placeholderTextColor={C.dim}
            placeholder={type === 'COMPLETION' ? '24 dia line erection completed in Unit 3.' : type === 'ISSUE' ? 'Radiography failed at joint 14, rework required.' : 'Trenching continued Km 2.0 to 2.4, 400 m today.'}
            style={s.note} />

          <View style={{ flexDirection: 'row', gap: 12, marginTop: 14 }}>
            <TouchableOpacity style={s.media} onPress={takePhoto}><Icon name="camera" size={18} color={C.text} /><Text style={s.mediaText}>{photoUri ? 'Retake Photo' : 'Take Photo'}</Text></TouchableOpacity>
            <TouchableOpacity style={[s.media, recording && { borderColor: C.red }]} onPress={toggleRecord}>
              <Icon name={recording ? 'square' : 'mic'} size={18} color={recording ? C.red : C.text} /><Text style={[s.mediaText, recording && { color: C.red }]}>{recording ? 'Stop' : audioUri ? 'Re-record' : 'Voice Note'}</Text>
            </TouchableOpacity>
          </View>
          {(photoUri || audioUri) && (
            <Card style={{ marginTop: 12, flexDirection: 'row', alignItems: 'center', gap: 14 }}>
              {photoUri ? <Image source={{ uri: photoUri }} style={s.thumb} /> : <View style={[s.thumb, { alignItems: 'center', justifyContent: 'center' }]}><Icon name="mic" size={24} color={C.muted} /></View>}
              <View style={{ flex: 1 }}>
                <Mono style={{ color: C.text }}>{photoUri ? 'site-photo.jpg' : 'voice-note.m4a'}{photoUri && audioUri ? ' + voice note' : ''}</Mono>
                <View style={{ flexDirection: 'row', alignItems: 'center', gap: 5, marginTop: 4 }}><Icon name="check" size={14} color={C.green} /><Text style={{ color: C.green, fontSize: 13 }}>Attached</Text></View>
              </View>
              <IconButton name="x" color={C.muted} onPress={() => { setPhotoUri(undefined); setAudioUri(undefined); }} />
            </Card>
          )}

          <Label style={{ marginTop: 26 }}>DISCIPLINE / AREA</Label>
          <View style={{ flexDirection: 'row', gap: 10 }}>
            <TouchableOpacity style={s.select} onPress={() => setDiscPicker(true)}>
              <Text style={s.selectText}>{discipline.replace('_', ' ')}</Text><Icon name="chevron-down" color={C.muted} size={18} />
            </TouchableOpacity>
            <TextInput value={area} onChangeText={setArea} placeholder="Unit 3 / Km 0 to 2" placeholderTextColor={C.dim} style={[s.select, { flex: 1.3 }, s.selectText]} />
          </View>

          <Label style={{ marginTop: 26 }}>{isAudit ? 'QUANTITY YOU VERIFIED ON SITE' : 'QUANTITY (OPTIONAL)'}</Label>
          <View style={{ flexDirection: 'row', gap: 10 }}>
            <TextInput value={quantity} onChangeText={setQuantity} keyboardType="numeric" placeholder="0" placeholderTextColor={C.dim} style={[s.select, { flex: 1 }, s.selectText]} />
            <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{ flex: 2 }} contentContainerStyle={{ gap: 6, alignItems: 'center' }}>
              {UNITS.map(u => (
                <TouchableOpacity key={u} onPress={() => setUnit(u)} style={[s.unit, unit === u && { borderColor: C.amber, backgroundColor: C.amberDim }]}>
                  <Text style={{ color: unit === u ? C.amber : C.muted, fontWeight: '600', fontSize: 13 }}>{u}</Text>
                </TouchableOpacity>
              ))}
            </ScrollView>
          </View>

          <Label style={{ marginTop: 26 }}>DATE & TIME</Label>
          <View style={s.select}><Mono style={{ color: C.text, fontSize: 16 }}>{whenText}</Mono><Text style={{ color: C.muted }}>now</Text></View>

          <Button title={isAudit ? 'Submit Audit' : 'Submit Observation'} icon={isAudit ? 'check-square' : 'send'} onPress={() => build(false)} style={{ marginTop: 34 }} />
          <Button title="Save as Draft" variant="text" onPress={() => build(true)} style={{ marginTop: 4 }} />
        </ScrollView>
      </KeyboardAvoidingView>

      <ActivityPicker visible={picker} activities={activities} onClose={() => setPicker(false)} onPick={chooseActivity} />
      <Modal visible={discPicker} transparent animationType="fade" onRequestClose={() => setDiscPicker(false)}>
        <TouchableOpacity style={s.backdrop} activeOpacity={1} onPress={() => setDiscPicker(false)}>
          <View style={s.sheet}>
            {DISCIPLINES.map(d => (
              <TouchableOpacity key={d} style={s.sheetRow} onPress={() => { setDiscipline(d); setDiscPicker(false); }}>
                <Text style={[s.selectText, d === discipline && { color: C.amber }]}>{d.replace('_', ' ')}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </TouchableOpacity>
      </Modal>
    </Screen>
  );
}

function ActivityPicker({ visible, activities, onClose, onPick }: { visible: boolean; activities: Activity[]; onClose: () => void; onPick: (a: Activity) => void }) {
  const [q, setQ] = useState('');
  const list = useMemo(() => {
    const t = q.trim().toLowerCase();
    return t ? activities.filter(a => a.activity_id.toLowerCase().includes(t) || a.activity_name.toLowerCase().includes(t) || (a.area_location || '').toLowerCase().includes(t)) : activities;
  }, [q, activities]);
  return (
    <Modal visible={visible} animationType="slide" onRequestClose={onClose}>
      <Screen>
        <Header title="SELECT ACTIVITY" onBack={onClose} />
        <View style={{ paddingHorizontal: 20 }}>
          <Input value={q} onChangeText={setQ} placeholder="Search ID, name or area" icon="search" autoFocus />
        </View>
        <FlatList data={list} keyExtractor={a => a.activity_id} contentContainerStyle={{ paddingHorizontal: 20, paddingBottom: 40 }}
          ListEmptyComponent={<Text style={{ color: C.muted, textAlign: 'center', marginTop: 40 }}>{activities.length ? 'No matches.' : 'No activities loaded. Pull to refresh on Today when online.'}</Text>}
          renderItem={({ item }) => (
            <TouchableOpacity onPress={() => onPick(item)}>
              <Card style={{ marginBottom: 10 }}>
                <Mono>{item.activity_id}</Mono>
                <Text style={{ color: C.text, fontSize: 16, fontWeight: '600', marginTop: 6 }}>{item.activity_name}</Text>
                <Mono style={{ fontSize: 12, marginTop: 6 }}>{item.discipline}{item.area_location ? ` · ${item.area_location}` : ''}</Mono>
              </Card>
            </TouchableOpacity>
          )} />
      </Screen>
    </Modal>
  );
}

const s = StyleSheet.create({
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 20, paddingVertical: 16, borderBottomWidth: 1, borderColor: C.border },
  back: { color: C.text, fontSize: 34, lineHeight: 34, width: 24 },
  title: { color: C.text, fontSize: 17, fontWeight: '800', letterSpacing: 3 },
  actName: { color: C.text, fontSize: 18, fontWeight: '600', marginTop: 6 },
  x: { color: C.muted, fontSize: 18, paddingHorizontal: 6 },
  chev: { color: C.muted, fontSize: 22 },
  note: { backgroundColor: C.surface, borderWidth: 1, borderColor: C.border, borderRadius: 6, padding: 16, color: C.text, fontSize: 17, minHeight: 150, textAlignVertical: 'top' },
  media: { flex: 1, flexDirection: 'row', gap: 8, borderWidth: 1, borderColor: C.border, backgroundColor: C.surface, borderRadius: 6, paddingVertical: 16, alignItems: 'center', justifyContent: 'center' },
  mediaText: { color: C.text, fontWeight: '600', fontSize: 15 },
  thumb: { width: 64, height: 64, borderRadius: 4, backgroundColor: C.surface2 },
  select: { flex: 1, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', backgroundColor: C.surface, borderWidth: 1, borderColor: C.border, borderRadius: 6, paddingHorizontal: 14, paddingVertical: 14 },
  selectText: { color: C.text, fontSize: 16 },
  unit: { paddingHorizontal: 12, paddingVertical: 10, borderRadius: 6, borderWidth: 1, borderColor: C.border, backgroundColor: C.surface },
  backdrop: { flex: 1, backgroundColor: 'rgba(0,0,0,0.7)', justifyContent: 'flex-end' },
  sheet: { backgroundColor: C.surface, borderTopWidth: 1, borderColor: C.border, paddingVertical: 8, paddingBottom: 30 },
  sheetRow: { paddingHorizontal: 24, paddingVertical: 16, borderBottomWidth: 1, borderColor: C.border },
});
