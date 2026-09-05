import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ScrollView } from 'react-native';
import { C } from '../lib/theme';
import { Settings } from '../lib/types';
import { checkHealth } from '../lib/api';

interface Props { settings: Settings; onChange: (s: Settings) => void; }

export function SettingsScreen({ settings, onChange }: Props) {
  const [status, setStatus] = useState<string>('');
  async function test() {
    setStatus('Checking...');
    const ok = await checkHealth(settings);
    setStatus(ok ? 'OK: backend reachable' : 'FAIL: cannot reach backend');
  }
  return (
    <ScrollView style={s.root} contentContainerStyle={{ padding: 16 }}>
      <Text style={s.h1}>Settings</Text>
      <Text style={s.label}>SATYA backend URL</Text>
      <TextInput style={s.input} value={settings.serverUrl} autoCapitalize="none" keyboardType="url"
        onChangeText={v => onChange({ ...settings, serverUrl: v })} placeholder="http://192.168.1.10:8000" placeholderTextColor={C.muted} />
      <Text style={s.hint}>Use 10.0.2.2 for the Android emulator, or your PC LAN IP on a real phone.</Text>
      <Text style={s.label}>Project ID</Text>
      <TextInput style={s.input} value={settings.projectId} autoCapitalize="characters" onChangeText={v => onChange({ ...settings, projectId: v })} />
      <Text style={s.label}>Your name / role</Text>
      <TextInput style={s.input} value={settings.author} onChangeText={v => onChange({ ...settings, author: v })} />
      <TouchableOpacity style={s.btn} onPress={test}><Text style={s.btnText}>Test connection</Text></TouchableOpacity>
      {!!status && <Text style={[s.hint, { color: status.startsWith('OK') ? C.green : C.red, marginTop: 10 }]}>{status}</Text>}

      <View style={s.about}>
        <Text style={s.aboutH}>SATYA Field Capture</Text>
        <Text style={s.aboutT}>Observations are stored on this device and pushed to the SATYA Execution Truth Layer when you sync. The backend extracts execution events, matches them to L5/L6 schedule activities, and routes low-confidence matches to a planner. Nothing here edits the schedule directly.</Text>
      </View>
    </ScrollView>
  );
}

const s = StyleSheet.create({
  root: { flex: 1, backgroundColor: C.bg },
  h1: { color: C.text, fontSize: 22, fontWeight: '700', letterSpacing: 1 },
  label: { color: C.muted, fontSize: 12, marginTop: 16, marginBottom: 6, textTransform: 'uppercase', letterSpacing: 1 },
  input: { backgroundColor: C.card, borderColor: C.border, borderWidth: 1, borderRadius: 8, color: C.text, padding: 12, fontSize: 15 },
  hint: { color: C.muted, fontSize: 12, marginTop: 6 },
  btn: { backgroundColor: C.accent, padding: 14, borderRadius: 8, alignItems: 'center', marginTop: 20 },
  btnText: { color: '#000', fontWeight: '800' },
  about: { marginTop: 32, padding: 14, backgroundColor: C.card, borderRadius: 10, borderWidth: 1, borderColor: C.border },
  aboutH: { color: C.accent, fontWeight: '700', marginBottom: 6 },
  aboutT: { color: C.muted, fontSize: 13, lineHeight: 19 },
});
