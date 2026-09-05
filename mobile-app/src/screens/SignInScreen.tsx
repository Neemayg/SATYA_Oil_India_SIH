import React, { useState } from 'react';
import { View, Text, ScrollView, StyleSheet, KeyboardAvoidingView, Platform } from 'react-native';
import { Screen, Icon, Input, Button, Label, Mono, Segmented } from '../components/ui';
import { C } from '../lib/theme';
import { Settings, Role } from '../lib/types';

export function SignInScreen({ settings, onSignIn }: { settings: Settings; onSignIn: (s: Settings) => void }) {
  const [name, setName] = useState(settings.name);
  const [crew, setCrew] = useState(settings.crew);
  const [project, setProject] = useState(settings.projectId);
  const [server, setServer] = useState(settings.serverUrl);
  const [role, setRole] = useState<Role>(settings.role || 'FIELD');
  const ok = name.trim().length > 1 && project.trim().length > 0;
  return (
    <Screen>
      <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
        <ScrollView contentContainerStyle={{ padding: 24, paddingTop: 80 }} keyboardShouldPersistTaps="handled">
          <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 10 }}><Icon name="git-branch" size={26} color={C.orange} /><Text style={s.logo}>S A T Y A</Text></View>
          <Text style={s.tag}>EXECUTION LINEAGE FOR FIELD OPERATIONS</Text>
          <View style={s.box}>
            <Label style={{ marginBottom: 22 }}>SIGN IN TO CONTINUE</Label>
            <Label>I AM A</Label>
            <View style={{ marginBottom: 18 }}><Segmented value={role} onChange={setRole} options={[{ key: 'FIELD', label: 'Field Engineer' }, { key: 'MANAGER', label: 'Site Manager' }]} /></View>
            <Input label="YOUR NAME" icon="user" value={name} onChangeText={setName} placeholder="M. Tran" />
            <Input label="CREW / DISCIPLINE" icon="users" value={crew} onChangeText={setCrew} placeholder="Field Crew 4 · Piping" />
            <Input label="PROJECT CODE" icon="hash" value={project} onChangeText={setProject} autoCapitalize="characters" placeholder="PRJ-NBG-2026" />
            <Input label="SATYA SERVER" icon="server" value={server} onChangeText={setServer} autoCapitalize="none" keyboardType="url" placeholder="http://192.168.1.10:8000" />
            <Button title="Sign In" disabled={!ok} onPress={() => onSignIn({ ...settings, signedIn: true, role, name: name.trim(), crew: crew.trim(), projectId: project.trim().toUpperCase(), serverUrl: server.trim() })} />
          </View>
          <Text style={s.help}>Need access? Contact your project administrator.</Text>
          <Mono style={{ marginTop: 40, fontSize: 11 }}>v1.0.0 · Oil India Limited · SIH 2026</Mono>
        </ScrollView>
      </KeyboardAvoidingView>
    </Screen>
  );
}

const s = StyleSheet.create({
  logo: { color: C.text, fontSize: 30, fontWeight: '800', letterSpacing: 4, textAlign: 'center' },
  tag: { color: C.muted, fontSize: 11, letterSpacing: 2, textAlign: 'center', marginTop: 8, marginBottom: 36 },
  box: { backgroundColor: C.surface, borderWidth: 1, borderColor: C.border, borderRadius: 6, padding: 22 },
  help: { color: C.muted, textAlign: 'center', marginTop: 28, fontSize: 13 },
});
