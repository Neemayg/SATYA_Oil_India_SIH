import React, { useState } from 'react';
import { View, Text, ScrollView, StyleSheet, Alert } from 'react-native';
import { Screen, Brand, Label, Mono, Input, Button, Card, Segmented, Badge } from '../components/ui';
import { C } from '../lib/theme';
import { Settings } from '../lib/types';
import { checkHealth } from '../lib/api';

interface Props { settings: Settings; stats: { total: number; pending: number; synced: number; activities: number }; onChange: (s: Settings) => void; onSync: () => void; onSignOut: () => void; }

export function ProfileScreen({ settings, stats, onChange, onSync, onSignOut }: Props) {
  const [status, setStatus] = useState('');
  async function test() {
    setStatus('Checking...');
    setStatus((await checkHealth(settings)) ? 'Connected to SATYA' : 'Cannot reach server. Check URL and Wi-Fi.');
  }
  const initials = settings.name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase() || 'FE';
  return (
    <Screen>
      <Brand />
      <ScrollView contentContainerStyle={{ padding: 20, paddingBottom: 60 }} keyboardShouldPersistTaps="handled">
        <Text style={s.h1}>PROFILE</Text>
        <View style={s.rule} />

        <View style={s.userRow}>
          <View style={s.avatar}><Text style={s.avatarText}>{initials}</Text></View>
          <View>
            <Text style={s.name}>{settings.name || 'Field Engineer'}</Text>
            <Mono>{settings.crew} · Project {settings.projectId}</Mono>
            <View style={{ marginTop: 6 }}><Badge text={settings.role === 'MANAGER' ? 'SITE MANAGER' : 'FIELD ENGINEER'} tone={settings.role === 'MANAGER' ? 'orange' : 'muted'} icon={settings.role === 'MANAGER' ? 'shield' : 'tool'} /></View>
          </View>
        </View>

        <View style={s.stats}>
          <Stat n={stats.total} l="LOGGED" />
          <Stat n={stats.synced} l="SYNCED" />
          <Stat n={stats.pending} l="PENDING" tone={stats.pending ? C.amber : undefined} />
          <Stat n={stats.activities} l="ACTIVITIES" />
        </View>

        <Card style={{ marginTop: 24 }}>
          <Label>CONNECTION</Label>
          <Input label="SATYA SERVER URL" icon="server" value={settings.serverUrl} autoCapitalize="none" keyboardType="url" onChangeText={v => onChange({ ...settings, serverUrl: v })} />
          <Input label="PROJECT CODE" icon="hash" value={settings.projectId} autoCapitalize="characters" onChangeText={v => onChange({ ...settings, projectId: v.toUpperCase() })} />
          <Text style={s.hint}>Default is the SATYA cloud server. Change only if running the backend locally.</Text>
          <View style={{ flexDirection: 'row', gap: 10, marginTop: 8 }}>
            <Button title="Test connection" icon="activity" variant="outline" onPress={test} style={{ flex: 1, paddingVertical: 13 }} />
            <Button title="Sync now" icon="refresh-cw" onPress={onSync} style={{ flex: 1, paddingVertical: 13 }} />
          </View>
          {!!status && <Text style={[s.status, { color: status.startsWith('Connected') ? C.green : status.startsWith('Checking') ? C.muted : C.red }]}>{status}</Text>}
        </Card>

        <Card style={{ marginTop: 16 }}>
          <Label>ACCOUNT</Label>
          <Label style={{ fontSize: 11 }}>ROLE</Label>
          <View style={{ marginBottom: 18 }}><Segmented value={settings.role} onChange={r => onChange({ ...settings, role: r })} options={[{ key: 'FIELD', label: 'Field Engineer' }, { key: 'MANAGER', label: 'Site Manager' }]} /></View>
          <Input label="NAME" icon="user" value={settings.name} onChangeText={v => onChange({ ...settings, name: v })} />
          <Input label="CREW / DISCIPLINE" icon="users" value={settings.crew} onChangeText={v => onChange({ ...settings, crew: v })} />
          <Button title="Sign out" icon="log-out" variant="danger" onPress={() => Alert.alert('Sign out?', 'Unsent observations stay on this device.', [{ text: 'Cancel' }, { text: 'Sign out', style: 'destructive', onPress: onSignOut }])} />
        </Card>

        <Text style={s.about}>Observations are stored on this phone first and sent to the SATYA Execution Truth Layer when you sync. The server extracts events, matches them to the L5/L6 schedule, and routes anything unclear to a planner. This app never edits the schedule.</Text>
      </ScrollView>
    </Screen>
  );
}

function Stat({ n, l, tone }: { n: number; l: string; tone?: string }) {
  return (
    <View style={s.stat}>
      <Text style={[s.statN, tone ? { color: tone } : null]}>{n}</Text>
      <Text style={s.statL}>{l}</Text>
    </View>
  );
}

const s = StyleSheet.create({
  h1: { color: C.text, fontSize: 28, fontWeight: '800', letterSpacing: 4, marginTop: 10 },
  rule: { height: 1, backgroundColor: C.border, marginTop: 18, marginBottom: 24 },
  userRow: { flexDirection: 'row', alignItems: 'center', gap: 16 },
  avatar: { width: 56, height: 56, borderRadius: 28, backgroundColor: C.orange, alignItems: 'center', justifyContent: 'center' },
  avatarText: { color: C.onPrimary, fontWeight: '800', fontSize: 18 },
  name: { color: C.text, fontSize: 20, fontWeight: '700', marginBottom: 4 },
  stats: { flexDirection: 'row', marginTop: 24, borderWidth: 1, borderColor: C.border, borderRadius: 6, backgroundColor: C.surface },
  stat: { flex: 1, alignItems: 'center', paddingVertical: 16, borderRightWidth: 1, borderColor: C.border },
  statN: { color: C.text, fontSize: 22, fontWeight: '800' },
  statL: { color: C.muted, fontSize: 10, letterSpacing: 1.5, marginTop: 4 },
  hint: { color: C.muted, fontSize: 12, marginTop: -8, marginBottom: 12 },
  status: { marginTop: 14, fontWeight: '600' },
  about: { color: C.dim, fontSize: 12, lineHeight: 18, marginTop: 24, textAlign: 'center' },
});
