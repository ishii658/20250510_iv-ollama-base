// 指定した tag に囲まれたコンテンツを分離します。

export function separateTagContent(input: string, tagName: string): [string | null, string | null] {
    // タグ名を正規表現に安全に変換
    const escapedTagName = tagName.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    
    // タグの内容を抽出する正規表現
    const regex = new RegExp(`<${escapedTagName}>([\s\S]*?)<\/${escapedTagName}>`);
    const tttMatch = input.match(regex);

    // タグ内の内容を取得（トリム）
    const tttContent = tttMatch ? tttMatch[1].trim() : null;

    // タグ以降の文字列を取得（トリム）
    let rest = null;
    if (tttMatch) {
        const fullMatch = tttMatch[0];
        if(tttMatch.index != undefined){
          const restStartIndex = tttMatch.index + fullMatch.length;
          rest = input.substring(restStartIndex).trim();
        }
    }

    return [tttContent, rest];
}

export function splitThinkContent(str: string): { thinkContent: string; afterThink: string } {
  const match = str.match(/<think>(.*?)<\/think>(.*)/s);
  if (match && match.length >= 3) {
    return {
      thinkContent: match[1],
      afterThink: match[2]
    };
  } else {
    return { thinkContent: '', afterThink: str };
  }
}