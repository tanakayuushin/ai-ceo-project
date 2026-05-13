import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Colors } from '../constants/colors';
import { useNavigation } from '@react-navigation/native';

interface Tool {
  id: string;
  title: string;
  subtitle: string;
  icon: string;
  color: string;
  tag?: string;
  action: string;
}

const TOOLS: Tool[] = [
  {
    id: '1',
    title: '経営計画書テンプレート',
    subtitle: '5年計画・単年度計画を作成',
    icon: 'document-text',
    color: Colors.accent,
    tag: '無料',
    action: 'chat',
  },
  {
    id: '2',
    title: '売上分析シート',
    subtitle: '月次・四半期の売上傾向を分析',
    icon: 'bar-chart',
    color: '#2196F3',
    tag: '無料',
    action: 'chat',
  },
  {
    id: '3',
    title: 'SWOT分析',
    subtitle: '自社の強み・弱み・機会・脅威',
    icon: 'grid',
    color: '#9C27B0',
    tag: 'AI生成',
    action: 'chat',
  },
  {
    id: '4',
    title: '補助金チェックリスト',
    subtitle: '申請前に確認すべき30のポイント',
    icon: 'checkbox',
    color: Colors.success,
    tag: '無料',
    action: 'subsidy',
  },
  {
    id: '5',
    title: 'SNS投稿文生成',
    subtitle: 'X/Instagram/Facebook投稿をAIが作成',
    icon: 'megaphone',
    color: '#FF9800',
    tag: 'AI生成',
    action: 'chat',
  },
  {
    id: '6',
    title: '営業メールテンプレート',
    subtitle: '新規・フォローアップ・クロージング',
    icon: 'mail',
    color: '#F44336',
    tag: 'AI生成',
    action: 'chat',
  },
  {
    id: '7',
    title: '会議アジェンダ作成',
    subtitle: '目的明確・時間管理された議題設定',
    icon: 'list',
    color: '#00BCD4',
    tag: 'AI生成',
    action: 'chat',
  },
  {
    id: '8',
    title: '採用面接質問集',
    subtitle: '職種・役職別の面接質問リスト',
    icon: 'people',
    color: '#607D8B',
    tag: '無料',
    action: 'chat',
  },
];

const AI_PROMPTS: Record<string, string> = {
  '1': '私の会社の経営計画書テンプレートを作ってください。業種、規模、目標を教えてください。',
  '2': '私の会社の売上分析シートのフォーマットを提案してください。',
  '3': '私の会社のSWOT分析をしたいです。業種と主なサービスを教えてください。',
  '4': '補助金申請前のチェックリストを作ってください。どの補助金を検討していますか？',
  '5': '自社のSNS投稿文を作ってください。業種、ターゲット、伝えたいことを教えてください。',
  '6': '営業メールのテンプレートを作ってください。どんなメールが必要ですか？',
  '7': '効果的な会議のアジェンダ作成を手伝ってください。会議の目的を教えてください。',
  '8': '採用面接で使える質問リストを作ってください。どんな人材を探していますか？',
};

function ToolCard({ tool, onPress }: { tool: Tool; onPress: () => void }) {
  return (
    <TouchableOpacity style={styles.toolCard} onPress={onPress}>
      <View style={[styles.toolIcon, { backgroundColor: tool.color + '22' }]}>
        <Ionicons name={tool.icon as any} size={26} color={tool.color} />
      </View>
      <View style={styles.toolInfo}>
        <View style={styles.toolTitleRow}>
          <Text style={styles.toolTitle}>{tool.title}</Text>
          {tool.tag && (
            <View style={[styles.toolTag, { backgroundColor: tool.color + '22' }]}>
              <Text style={[styles.toolTagText, { color: tool.color }]}>{tool.tag}</Text>
            </View>
          )}
        </View>
        <Text style={styles.toolSubtitle}>{tool.subtitle}</Text>
      </View>
      <Ionicons name="chevron-forward" size={18} color={Colors.textMuted} />
    </TouchableOpacity>
  );
}

export default function ToolsScreen() {
  const navigation = useNavigation<any>();

  const handleToolPress = (tool: Tool) => {
    if (tool.action === 'subsidy') {
      navigation.navigate('Subsidy');
    } else {
      navigation.navigate('Chat', { initialMessage: AI_PROMPTS[tool.id] });
    }
  };

  return (
    <View style={styles.container}>
      {/* ヘッダー */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>経営ツール</Text>
        <Text style={styles.headerSub}>AIが即座にサポート</Text>
      </View>

      <ScrollView showsVerticalScrollIndicator={false} style={styles.body}>
        {/* バナー */}
        <View style={styles.banner}>
          <Ionicons name="sparkles" size={18} color={Colors.accent} />
          <Text style={styles.bannerText}>
            各ツールをタップすると、AIが専用の質問をして自動で書類を作成します
          </Text>
        </View>

        <Text style={styles.sectionTitle}>すべてのツール</Text>
        {TOOLS.map((tool) => (
          <ToolCard
            key={tool.id}
            tool={tool}
            onPress={() => handleToolPress(tool)}
          />
        ))}

        {/* カスタム相談 */}
        <View style={styles.customCard}>
          <Ionicons name="add-circle" size={24} color={Colors.accent} />
          <View style={{ flex: 1 }}>
            <Text style={styles.customTitle}>その他の相談</Text>
            <Text style={styles.customSubtitle}>
              リストにない課題もAIに相談できます
            </Text>
          </View>
          <TouchableOpacity
            style={styles.customBtn}
            onPress={() => navigation.navigate('Chat')}
          >
            <Text style={styles.customBtnText}>相談する</Text>
          </TouchableOpacity>
        </View>

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
    color: Colors.textSecondary,
    fontSize: 12,
    marginTop: 2,
  },
  body: {
    flex: 1,
    padding: 16,
  },
  banner: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 8,
    backgroundColor: Colors.primary,
    borderRadius: 12,
    padding: 14,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: Colors.accent + '44',
  },
  bannerText: {
    color: Colors.textSecondary,
    fontSize: 12,
    flex: 1,
    lineHeight: 18,
  },
  sectionTitle: {
    color: Colors.textSecondary,
    fontSize: 12,
    fontWeight: '600',
    letterSpacing: 0.5,
    textTransform: 'uppercase',
    marginBottom: 12,
  },
  toolCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.surface,
    borderRadius: 14,
    padding: 14,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: Colors.border,
    gap: 12,
  },
  toolIcon: {
    width: 50,
    height: 50,
    borderRadius: 14,
    justifyContent: 'center',
    alignItems: 'center',
  },
  toolInfo: {
    flex: 1,
  },
  toolTitleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 3,
  },
  toolTitle: {
    color: Colors.text,
    fontSize: 14,
    fontWeight: '600',
  },
  toolTag: {
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 10,
  },
  toolTagText: {
    fontSize: 10,
    fontWeight: '600',
  },
  toolSubtitle: {
    color: Colors.textSecondary,
    fontSize: 12,
  },
  customCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.surface,
    borderRadius: 14,
    padding: 16,
    marginTop: 4,
    borderWidth: 1,
    borderColor: Colors.accent + '44',
    gap: 12,
  },
  customTitle: {
    color: Colors.text,
    fontSize: 14,
    fontWeight: '600',
  },
  customSubtitle: {
    color: Colors.textSecondary,
    fontSize: 12,
    marginTop: 2,
  },
  customBtn: {
    backgroundColor: Colors.accent,
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
  },
  customBtnText: {
    color: Colors.background,
    fontSize: 13,
    fontWeight: '700',
  },
});
