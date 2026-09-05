import React from 'react';
import { View, Text, TouchableOpacity, TextInput, StyleSheet, ViewStyle, TextInputProps, TextStyle } from 'react-native';
import { Feather } from '@expo/vector-icons';
import { C, MONO, R } from '../lib/theme';

export type IconName = React.ComponentProps<typeof Feather>['name'];
export const Icon = ({ name, size = 18, color = C.text, style }: { name: IconName; size?: number; color?: string; style?: ViewStyle }) => (
  <Feather name={name} size={size} color={color} style={style} />
);

export const Screen = ({ children }: { children: React.ReactNode }) => <View style={{ flex: 1, backgroundColor: C.bg }}>{children}</View>;

export function Brand({ right }: { right?: React.ReactNode }) {
  return (
    <View style={s.brandRow}>
      <Text style={s.brand}>S A T Y A</Text>
      {right}
    </View>
  );
}

export function Header({ title, onBack, right }: { title: string; onBack?: () => void; right?: React.ReactNode }) {
  return (
    <View style={s.header}>
      {onBack ? <IconButton name="arrow-left" onPress={onBack} /> : <View style={{ width: 40 }} />}
      <Text style={s.headerTitle}>{title}</Text>
      {right ?? <View style={{ width: 40 }} />}
    </View>
  );
}

export function IconButton({ name, onPress, color = C.text, size = 20 }: { name: IconName; onPress: () => void; color?: string; size?: number }) {
  return (
    <TouchableOpacity onPress={onPress} hitSlop={10} style={s.iconBtn}>
      <Icon name={name} size={size} color={color} />
    </TouchableOpacity>
  );
}

export function Label({ children, style }: { children: React.ReactNode; style?: TextStyle }) {
  return <Text style={[s.label, style]}>{children}</Text>;
}

export function Mono({ children, style, numberOfLines }: { children: React.ReactNode; style?: TextStyle; numberOfLines?: number }) {
  return <Text numberOfLines={numberOfLines} style={[{ fontFamily: MONO, color: C.muted, fontSize: 13 }, style]}>{children}</Text>;
}

export type Tone = 'amber' | 'green' | 'red' | 'muted' | 'orange';
const toneColor: Record<Tone, string> = { amber: C.amber, green: C.green, red: C.red, muted: C.muted, orange: C.orange };
const toneBg: Record<Tone, string> = { amber: C.amberDim, green: C.greenDim, red: C.redDim, muted: C.surface2, orange: C.amberDim };

export function Badge({ text, tone = 'muted', filled, icon }: { text: string; tone?: Tone; filled?: boolean; icon?: IconName }) {
  const color = toneColor[tone];
  return (
    <View style={[s.badge, { borderColor: color, backgroundColor: filled ? toneBg[tone] : 'transparent' }]}>
      {icon && <Icon name={icon} size={11} color={color} style={{ marginRight: 5 }} />}
      <Text style={[s.badgeText, { color }]}>{text}</Text>
    </View>
  );
}

export function Button({ title, onPress, variant = 'primary', disabled, style, icon }:
  { title: string; onPress: () => void; variant?: 'primary' | 'outline' | 'text' | 'danger'; disabled?: boolean; style?: ViewStyle; icon?: IconName }) {
  const box: ViewStyle = variant === 'primary' ? { backgroundColor: C.orange }
    : variant === 'outline' ? { backgroundColor: C.surface, borderWidth: 1, borderColor: C.border }
    : variant === 'danger' ? { backgroundColor: C.redDim, borderWidth: 1, borderColor: C.red }
    : { backgroundColor: 'transparent' };
  const color = variant === 'primary' ? C.onPrimary : variant === 'danger' ? C.red : variant === 'text' ? C.muted : C.text;
  return (
    <TouchableOpacity onPress={onPress} disabled={disabled} activeOpacity={0.8} style={[s.btn, box, disabled && { opacity: 0.4 }, style]}>
      {icon && <Icon name={icon} size={17} color={color} style={{ marginRight: 8 }} />}
      <Text style={[s.btnText, { color }]}>{title}</Text>
    </TouchableOpacity>
  );
}

export function Input(props: TextInputProps & { label?: string; icon?: IconName }) {
  return (
    <View style={{ marginBottom: 18 }}>
      {!!props.label && <Label>{props.label}</Label>}
      <View>
        {props.icon && <Icon name={props.icon} size={16} color={C.muted} style={s.inputIcon} />}
        <TextInput placeholderTextColor={C.dim} {...props} style={[s.input, props.icon && { paddingLeft: 42 }, props.style]} />
      </View>
    </View>
  );
}

export function Segmented<T extends string>({ options, value, onChange }: { options: { key: T; label: string }[]; value: T; onChange: (v: T) => void }) {
  return (
    <View style={s.seg}>
      {options.map(o => (
        <TouchableOpacity key={o.key} onPress={() => onChange(o.key)} style={[s.segItem, value === o.key && s.segOn]}>
          <Text style={[s.segText, value === o.key && { color: C.text }]}>{o.label}</Text>
        </TouchableOpacity>
      ))}
    </View>
  );
}

export function Card({ children, style, accent }: { children: React.ReactNode; style?: ViewStyle; accent?: string }) {
  return <View style={[s.card, accent ? { borderLeftWidth: 3, borderLeftColor: accent } : null, style]}>{children}</View>;
}

export function ListRow({ icon, title, subtitle, right, onPress }: { icon?: IconName; title: string; subtitle?: string; right?: React.ReactNode; onPress?: () => void }) {
  return (
    <TouchableOpacity disabled={!onPress} onPress={onPress} activeOpacity={0.8} style={s.listRow}>
      {icon && <View style={s.listIcon}><Icon name={icon} size={18} color={C.muted} /></View>}
      <View style={{ flex: 1 }}>
        <Text style={s.listTitle} numberOfLines={1}>{title}</Text>
        {!!subtitle && <Text style={s.listSub} numberOfLines={1}>{subtitle}</Text>}
      </View>
      {right}
    </TouchableOpacity>
  );
}

const TABS: { key: string; label: string; icon: IconName }[] = [
  { key: 'today', label: 'TODAY', icon: 'calendar' },
  { key: 'capture', label: 'CAPTURE', icon: 'camera' },
  { key: 'reports', label: 'REPORTS', icon: 'file-text' },
  { key: 'profile', label: 'PROFILE', icon: 'user' },
];

export function TabBar({ active, onChange, badge }: { active: string; onChange: (k: any) => void; badge?: number }) {
  return (
    <View style={s.tabBar}>
      {TABS.map(t => {
        const on = active === t.key;
        const color = on ? C.orange : C.muted;
        return (
          <TouchableOpacity key={t.key} style={s.tab} onPress={() => onChange(t.key)}>
            <View>
              <Icon name={t.icon} size={22} color={color} />
              {t.key === 'reports' && !!badge && <View style={s.dot}><Text style={s.dotText}>{badge}</Text></View>}
            </View>
            <Text style={[s.tabLabel, { color }]}>{t.label}</Text>
          </TouchableOpacity>
        );
      })}
    </View>
  );
}

const s = StyleSheet.create({
  brandRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingHorizontal: 20, paddingTop: 18, paddingBottom: 12 },
  brand: { color: C.text, fontSize: 18, fontWeight: '800', letterSpacing: 2 },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 12, paddingVertical: 10, borderBottomWidth: 1, borderColor: C.border },
  headerTitle: { color: C.text, fontSize: 16, fontWeight: '800', letterSpacing: 3 },
  iconBtn: { width: 40, height: 40, alignItems: 'center', justifyContent: 'center', borderRadius: 20 },
  label: { color: C.muted, fontSize: 12, letterSpacing: 2, fontWeight: '600', marginBottom: 10 },
  badge: { flexDirection: 'row', alignItems: 'center', borderWidth: 1, paddingHorizontal: 9, paddingVertical: 5, borderRadius: R },
  badgeText: { fontSize: 11, fontWeight: '700', letterSpacing: 1.2 },
  btn: { flexDirection: 'row', paddingVertical: 16, paddingHorizontal: 20, borderRadius: R, alignItems: 'center', justifyContent: 'center' },
  btnText: { fontSize: 16, fontWeight: '700' },
  input: { backgroundColor: C.surface, borderWidth: 1, borderColor: C.border, borderRadius: R, paddingHorizontal: 14, paddingVertical: 15, fontSize: 16, color: C.text },
  inputIcon: { position: 'absolute', left: 14, top: 17, zIndex: 1 },
  seg: { flexDirection: 'row', borderWidth: 1, borderColor: C.border, borderRadius: R, overflow: 'hidden' },
  segItem: { flex: 1, paddingVertical: 14, alignItems: 'center', backgroundColor: C.bg },
  segOn: { backgroundColor: C.surface2 },
  segText: { color: C.muted, fontSize: 15, fontWeight: '600' },
  card: { backgroundColor: C.surface, borderWidth: 1, borderColor: C.border, borderRadius: R, padding: 16 },
  listRow: { flexDirection: 'row', alignItems: 'center', gap: 12, paddingVertical: 14, borderBottomWidth: 1, borderColor: C.border },
  listIcon: { width: 36, height: 36, borderRadius: 8, backgroundColor: C.surface2, alignItems: 'center', justifyContent: 'center' },
  listTitle: { color: C.text, fontSize: 15, fontWeight: '600' },
  listSub: { color: C.muted, fontSize: 13, marginTop: 2 },
  tabBar: { flexDirection: 'row', borderTopWidth: 1, borderColor: C.border, backgroundColor: C.bg, paddingBottom: 6 },
  tab: { flex: 1, alignItems: 'center', paddingTop: 12, paddingBottom: 8, gap: 6 },
  tabLabel: { fontSize: 10, letterSpacing: 1.5, fontWeight: '600' },
  dot: { position: 'absolute', top: -5, right: -12, backgroundColor: C.orange, minWidth: 16, height: 16, borderRadius: 8, alignItems: 'center', justifyContent: 'center', paddingHorizontal: 3 },
  dotText: { color: C.onPrimary, fontSize: 9, fontWeight: '800' },
});
