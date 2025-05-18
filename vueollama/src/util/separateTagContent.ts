// 指定した tag に囲まれたコンテンツを分離します。

export function separateTagContent(input: string, tagName: string): [ string | null, string | null ] {
    // Escape the tag name for use in a regular expression
    const escapedTagName = tagName.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

    // Construct regex to match the opening and closing tags
    const regex = new RegExp(`<${escapedTagName}>([\s\S]*?)<\/${escapedTagName}>`);
    const tttMatch = input.match(regex);

    // Extract the content between the tags
    const tttContent = tttMatch ? tttMatch[1].trim() : null;

    // Find the index of the closing tag
    const closingTag = `</${tagName}>`;
    const closingTagIndex = input.indexOf(closingTag);

    // Extract the rest of the string after the closing tag
    let rest = null;
    if (closingTagIndex !== -1) {
        rest = input.substring(closingTagIndex + closingTag.length).trim();
    }

    return [ tttContent, rest ];
}