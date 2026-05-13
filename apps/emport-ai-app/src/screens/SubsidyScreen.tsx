import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Linking,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Colors } from '../constants/colors';

interface SubsidyItem {
  id: string;
  name: string;
  amount: string;
  ratio: string;
  deadline: string;
  target: string;
  description: string;
  url: string;
  tag: string;
  tagColor: string;
}

const SUBSIDIES: SubsidyItem[] = [
  {
    id: '1',
    name: 'デジタル化AI導入補助金 2026',
    amount: '最大450万円',
    ratio: '補助率 2/3',
    deadline: '2026年7月（次回締切）',
    target: '中小企業・小規模事業者',
    description:
      'AI・ITシステム導入、業務自動化、デジタルマーケティング強化などが対象。複数回締切あり。',
    url: 'https://it-shien.smrj.go.jp/',
    tag: '注目',
    tagColor: Colors.accent,
  },
  {
    id: '2',
    name: 'ものづくり・商業・サービス生産性向上促進補助金',
    amount: '最大1,250万円',
    ratio: '補助率 1/2〜2/3',
    deadline: '2026年6月（予定）',
    target: '中小企業',
    description:
      '革新的なサービス開発・試作品開発・生産プロセスの改善を行う設備投資等を支援。AI活用枠あり。',
    url: 'https://portal.monodukuri-hojo.jp/',
    tag: '大型',
    tagColor: '#9C27B0',
  },
  {
    id: '3',
    name: '小規模事業者持続化補助金',
    amount: '最大200万円',
    ratio: '補助率 2/3',
    deadline: '2026年5月（第17回）',
    target: '小規模事業者',
    description:
      'ホームページ制作、チラシ印刷、設備購入など販路開拓全般が対象。申請しやすく人気が高い。',
    url: 'https://s23.jizokukahojokin.info/',
    tag: '申請しやすい',
    tagColor: Colors.success,
  },
  {
    id: '4',
    name: 'やまぐち産業振興財団 DX推進補助',
    amount: '上限50万円',
    ratio: '補助率 1/2',
    deadline: '随時受付',
    target: '山口県内中小企業',
    description:
      'RPA・クラウド・AI・ビジネスチャット等のITツール導入費を補助。山口県内企業向けの地域補助金。',
    url: 'https://www.ymg-zaidan.or.jp/',
    tag: '山口県',
    tagColor: '#2196F3',
  },
  {
    id: '5',
    name: '事業再構築補助金',
    amount: '最大3,000万円',
    ratio: '補助率 1/2〜2/3',
    deadline: '2026年度受付中',
    target: '中小企業・中堅企業',
    description:
      'コロナ禍や社会変化に対応した新事業展開・業種転換・事業再編等の大規模投資を支援。',
    url: 'https://jigyou-saikouchiku.go.jp/',
    tag: '大型',
    tagColor: '#9C27B0',
  },
];

function SubsidyCard({ item }: { item: SubsidyItem }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <View style={styles.card}>
      <TouchableOpacity onPress={() => setExpanded(!expanded)}>
        <View style={styles.cardHeader}>
          <View style={[styles.tag, { backgroundColor: item.tagColor + '22' }]}>
            <Text style={[styles.tagText, { color: item.tagColor }]}>{item.tag}</Text>
          </View>
          <Ionicons
            name={expanded ? 'chevron-up' : 'chevron-down'}
            size={18}
            color={Colors.textSecondary}
          />
        </View>
        <Text style={styles.cardName}>{item.name}</Text>
        <View style={styles.cardAmounts}>
          <View style={styles.amountBadge}>
            <Ionicons name="cash" size={14} color={Colors.accent} />
            <Text style={styles.amountText}>{item.amount}</Text>
          </View>
          <View style={styles.ratioBadge}>
            <Text style={styles.ratioText}>{item.ratio}</Text>
          </View>
        </View>
        <View style={styles.deadlineRow}>
          <Ionicons name="calendar" size={13} color={Colors.textMuted} />
          <Text style={styles.deadlineText}>{item.deadline}</Text>
        </View>
      </TouchableOpacity>

      {expanded && (
        <View style={styles.expandedContent}>
          <View style={styles.separator} />
          <Text style={styles.targetLabel}>対象</Text>
          <Text style={styles.targetText}>{item.target}</Text>
          <Text style={styles.descText}>{item.description}</Text>
          <TouchableOpacity
            style={styles.linkBtn}
            onPress={() => Linking.openURL(item.url)}
          >
            <Text style={styles.linkText}>詳細を確認する</Text>
            <Ionicons name="open-outline" size={14} color={Colors.accent} />
          </TouchableOpacity>
        </View>
      )}
    </View>
  );
}

export default function SubsidyScreen() {
  return (
    <View style={styles.container}>
      {/* ヘッダー */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>補助金情報</Text>
        <Text style={styles.headerSub}>2026年度 最新情報</Text>
      </View>

      {/* バナー */}
      <View style={styles.banner}>
        <Ionicons name="information-circle" size={20} color={Colors.accent} />
        <Text style={styles.bannerText}>
          AIチャットで「どの補助金が合う？」と聞くと、あなたの業種に合った補助金を提案します。
        </Text>
      </View>

      <ScrollView showsVerticalScrollIndicator={false} style={styles.body}>
        {SUBSIDIES.map((item) => (
          <SubsidyCard key={item.id} item={item} />
        ))}
        <View style={{ height: 30 }} />
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  header: {
    paddingTop: 50,
    paddingBottom: 16,
    paddingHorizontal: 16,
    backgroundColor: Colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  headerTitle: {
    color: Colors.text,
    fontSize: 22,
    fontWeight: 'bold',
  },
  headerSub: {
    color: Colors.accent,
    fontSize: 12,
    marginTop: 2,
  },
  banner: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 8,
    backgroundColor: Colors.primary,
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  bannerText: {
    color: Colors.textSecondary,
    fontSize: 12,
    flex: 1,
    lineHeight: 18,
  },
  body: {
    padding: 16,
  },
  card: {
    backgroundColor: Colors.surface,
    borderRadius: 14,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 6,
  },
  tag: {
    paddingHorizontal: 10,
    paddingVertical: 3,
    borderRadius: 20,
  },
  tagText: {
    fontSize: 11,
    fontWeight: '600',
  },
  cardName: {
    color: Colors.text,
    fontSize: 14,
    fontWeight: '600',
    lineHeight: 20,
    marginBottom: 10,
  },
  cardAmounts: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 6,
  },
  amountBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    backgroundColor: Colors.accent + '22',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 8,
  },
  amountText: {
    color: Colors.accent,
    fontSize: 13,
    fontWeight: '700',
  },
  ratioBadge: {
    backgroundColor: Colors.border,
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 8,
  },
  ratioText: {
    color: Colors.textSecondary,
    fontSize: 12,
  },
  deadlineRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  deadlineText: {
    color: Colors.textMuted,
    fontSize: 11,
  },
  separator: {
    height: 1,
    backgroundColor: Colors.border,
    marginVertical: 12,
  },
  expandedContent: {},
  targetLabel: {
    color: Colors.textMuted,
    fontSize: 11,
    marginBottom: 2,
  },
  targetText: {
    color: Colors.text,
    fontSize: 13,
    fontWeight: '600',
    marginBottom: 8,
  },
  descText: {
    color: Colors.textSecondary,
    fontSize: 13,
    lineHeight: 20,
    marginBottom: 12,
  },
  linkBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    alignSelf: 'flex-start',
    backgroundColor: Colors.accent + '22',
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 20,
  },
  linkText: {
    color: Colors.accent,
    fontSize: 13,
    fontWeight: '600',
  },
});
