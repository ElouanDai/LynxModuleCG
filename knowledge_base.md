## 1 第一章：模块解析规则深度说明
本章深入探讨了 JavaScript 模块解析的技术细节，解释了其工作原理和规则。

### 1.1. 核心基石：`package.json`
`package.json` 文件是每个 Node.js 项目或库的核心，扮演着“包清单”的角色。它不仅定义了项目的元数据（如名称、版本），还通过特定的字段指导 Node.js 和前端构建工具如何找到并加载模块的入口文件。理解这些字段是掌握模块解析的第一步。

### 1.2. 现代模块解析：`exports` 字段 (The Authoritative Rule)
`exports` 字段是 Node.js 引入的现代化模块入口定义方式，它的出现彻底改变了模块解析的规则。

- **最高优先级**: 一旦 `package.json` 中存在 `exports` 字段，所有传统的入口字段（如 `main`、`module`、`browser` 等）都将被完全忽略。`exports` 提供了唯一的、权威的解析规则。

- **版本支持**: `exports` 字段在 **Node.js v12.17.0** 及更高版本中受支持。在需要兼容旧版 Node.js 的项目中，开发者仍需提供传统入口字段作为后备。

- **核心功能**:
	- **强封装性**: `exports` 字段通过明确定义包的公共 API，阻止了对包内部文件的“深度导入”。例如，如果一个文件没有在 `exports` 中被导出，用户将无法直接 `require(\'pkg/internal/feature.js\')`，从而保护了库的内部结构，避免了意外的破坏性更改。
	- **条件导出 (Conditional Exports)**: 这是 `exports` 最强大的功能之一，允许包作者根据不同的使用场景提供不同的模块实现。
		- **条件解析顺序**: 当一个导入发生时，Node.js 会按照严格的顺序解析这些条件，并使用第一个匹配的路径。这个顺序是：
			1. `\"import\"` - 当模块通过 ES Module 的 `import` 语句或 `import()` 表达式加载时匹配。
			2. `\"require\"` - 当模块通过 CommonJS 的 `require()` 函数加载时匹配。
			3. `\"node\"` - 匹配任意 Node.js 环境。
			4. `\"browser\"` - 匹配任意浏览器环境（由构建工具支持）。
			5. `\"default\"` - 作为最后的兜底选项，当以上所有条件都不匹配时使用。
		- **示例**:
		```json
\"exports\": {
  \".\": {
    \"import\": \"./dist/index.mjs\",
    \"require\": \"./dist/index.cjs\"
  },
  \"./feature\": \"./dist/feature.js\"
}
```
		在这个例子中：
			- `import \'pkg\'` 会加载 `index.mjs`。
			- `require(\'pkg\')` 会加载 `index.cjs`。
			- `import \'pkg/feature\'` 会加载 `feature.js`。
		- **错误处理**: 如果 `exports` 中定义的路径无效或文件不存在，Node.js 会抛出一个明确的错误，如 `ERR_MODULE_NOT_FOUND` 或 `ERR_PACKAGE_PATH_NOT_EXPORTED`，这极大地简化了调试过程。

### 1.3. 模块系统定义：`type` 字段的影响
`package.json` 中的 `type` 字段决定了包内 `.js` 文件默认被当作哪种模块系统来解析，这直接影响 `exports` 和其他字段的行为。

- `\"type\": \"module\"`: 包内所有的 `.js` 文件都将被视为 ES Module (ESM)。

- `\"type\": \"commonjs\"`: (默认值) 包内所有的 `.js` 文件都将被视为 CommonJS (CJS) 模块。

开发者可以通过文件扩展名来覆盖 `type` 字段的默认行为：

- `.mjs` 文件始终被视为 ESM。

- `.cjs` 文件始终被视为 CJS。

### 1.4. 传统回退机制 (Legacy Fallback Rules)
**仅当&nbsp;****exports****&nbsp;字段不存在时**，Node.js 和构建工具才会启用传统的后备解析规则。

- **平台特定字段**:
	- **目的**: 这些字段允许库为特定的运行环境（如浏览器、移动端）提供专门优化的代码。
	- **非标准性**: 必须注意，除了 `browser` 之外，大多数平台字段（如 `lynx`, `react-native`, `electron`）都是 **非标准** 的。它们依赖于特定构建工具（如 Webpack, Vite）或运行时环境的扩展支持才能生效。
	- **browser****&nbsp;字段高级用法**: `browser` 字段不仅可以指定浏览器环境的入口文件，还可以用于替换或排除特定模块。这在适配仅存在于 Node.js 环境的模块（如 `fs`）时非常有用。
	```json
\"browser\": {
  \"./lib/node-specific.js\": \"./lib/browser-version.js\",
  \"fs\": false
}
```
		- 上例中，当在浏览器环境导入 `./lib/node-specific.js` 时，实际会加载 `./lib/browser-version.js`。
		- `require(\'fs\')` 将会得到一个空对象，从而避免了在浏览器中引用不存在的模块而导致的错误。

- **标准入口字段**:
	- `module`: 指向一个 ESM (ES Module) 入口。现代构建工具（如 Webpack, Vite）会优先使用此字段，因为它有利于进行 Tree Shaking（摇树优化），从而减小最终打包体积。
	- `main`: 这是最古老、最通用的入口字段，指向一个 CJS (CommonJS) 入口，作为最后的兜底选项，确保了在所有环境中的兼容性。

### 1.5. 边缘情况解析 (Edge Case Analysis)
- **package.json****&nbsp;缺失**: 如果一个目录中没有 `package.json` 文件，当尝试从该目录导入模块时，Node.js 会按照默认规则查找 `index.js`。如果包的 `type` 被设定为 `\"module\"`，则会查找 `index.mjs`。

## 2 第二章：实践应用：如何精准筛选模块实现
本章将第一章的理论知识转化为一个实践性的分步指南，帮助开发者在面对一个 npm 包时，能够快速准确地判断出究竟哪个文件会被加载。

### 2.1. 筛选流程概览
当一个模块被导入时，Node.js 或构建工具会像一个侦探，遵循一套严格的线索（`package.json` 中的字段）来寻找正确的文件。你可以将这个过程想象成一个决策流程图：

### 2.2. 第一步：检查 `exports` 字段
这是你首先需要检查的地方。如果 `package.json` 中存在 `exports` 字段，那么恭喜你，你的搜索范围大大缩小了。`exports` 字段是决定性的，它完全定义了包的入口。你只需要：

1. **确认导入方式**: 你是使用 `import` (ESM) 还是 `require` (CJS)？

2. **查看条件**: 在 `exports` 字段中找到与你的导入方式和环境（`node`, `browser` 等）匹配的条件。

3. **定位文件**: 该条件对应的值就是最终会被加载的文件路径。

一旦 `exports` 存在，你就可以完全忽略 `main`, `module`, `browser` 等所有其他字段。

### 2.3. 第二步：(若无`exports`) 检查平台特定实现
如果 `package.json` 中没有 `exports` 字段，解析器会进入传统的回退模式。此时，你需要检查是否存在为你的目标环境量身定制的字段。

- 如果你在为 **浏览器** 开发，查找 `browser` 字段。

- 如果你在为 **Lynx 环境** 开发，查找 `lynx` 字段。

- 以此类推，匹配你的目标平台（`react-native`, `electron` 等）。

如果找到了匹配的平台字段，那么它指向的文件就是你需要的实现。

- **为什么需要平台特异性实现？**不同运行环境（如浏览器、React Native、微信小程序）拥有不同的全局 API、能力和限制。例如，浏览器环境有 `window` 对象，而 Node.js 则有 `process` 对象。为了充分利用平台优势或规避平台限制，库的开发者会提供功能相同但实现方式不同的代码。

- **如何配置？**平台特异性实现是在**第三方库的&nbsp;****package.json****&nbsp;文件中**通过添加特定字段来声明的。构建工具或运行时在解析模块时，会识别这些字段并优先选择。

- **常见的平台特定字段集合**

| 平台字段<br> | 适用环境<br> | 说明<br> | 
| --- | --- | --- | 
| `browser`<br> | 浏览器环境<br> | 提供浏览器特定的实现，常用于替代 Node.js 核心模块的功能。<br> | 
| `react-native`<br> | React Native 应用<br> | 为 React Native 环境提供特定的原生模块桥接或组件实现。<br> | 
| `lynx`<br> | 字节跳动 Lynx 框架<br> | 为字节跳动的 Lynx 跨平台框架提供特定实现。<br> | 
| `electron`<br> | Electron 应用<br> | 分为主进程 (`electron`) 和渲染进程 (`browser`) 的实现。<br> | 
| `wechat-miniprogram`<br> | 微信小程序<br> | 为微信小程序环境提供特定实现，适配其独特的 API 和生命周期。<br> | 

### 2.4. 第三步：(若无前两者) 区分 ESM 与 CJS 实现
如果既没有 `exports` 字段，也没有找到与你环境匹配的平台特定字段，那么解析器会最后诉诸于标准的 `module` 和 `main` 字段。

- **优先&nbsp;****module**: 如果你使用的工具链支持 ES Modules（例如 Webpack, Vite, Rollup 等现代构建工具），它会优先查找并使用 `module` 字段指向的文件。这通常是一个 ESM 格式的文件，有利于进行 Tree Shaking。

- **后备&nbsp;****main**: 如果 `module` 字段不存在，或者环境不支持 ESM，那么 `main` 字段将作为最终的兜底选项。它指向一个 CommonJS 格式的文件，保证了最大的兼容性。

在完成了平台筛选之后，如果不存在平台特定的版本，解析器会进入第二个筛选维度：选择使用 CommonJS (CJS) 还是 ES Modules (ESM) 规范的实现。

- **module****&nbsp;(ESM) - 现代首选**现代构建工具（如 Webpack, Rollup）会优先查找 `package.json` 中的 `module` 字段。该字段指向一个使用 `import`/`export` 语法的 ES Module 文件。
	- **优点**：ESM 的静态特性使得构建工具可以在编译时进行深入的静态分析，从而实现 **Tree Shaking**（摇树优化）。这意味着如果你的代码只用到了库中的一小部分功能，未被引用的代码将不会被打包进最终的产物，有效减小应用的体积。

- **main****&nbsp;(CJS) - 通用后备**如果 `module` 字段不存在，或者环境不支持 ESM（例如某些旧版本的 Node.js），解析器会回退到使用 `main` 字段。该字段通常指向一个使用 `require`/`module.exports` 语法的 CommonJS 文件。
	- **优点**：CJS 具有最广泛的兼容性，是 Node.js 长期以来的标准模块系统，能够确保库在各种环境下都能正常工作。

**总结来说，CJS vs. ESM 的筛选逻辑是：** 优先尝试 `module` 以获取 Tree Shaking 的优化，如果不行则回退到 `main` 以保证兼容性。

### 2.5. 特别注意：构建工具的自定义行为
在真实的项目中，模块解析的最终行为可能会受到构建工具配置的影响。例如，Webpack 允许通过 `resolve.mainFields` 选项来自定义传统入口字段的解析优先级。默认情况下，它的顺序可能是 `[\'browser\', \'module\', \'main\']`，但你可以修改这个顺序来满足特殊的项目需求。

```javascript
// webpack.config.js
module.exports = {
  //...
  resolve: {
    mainFields: [\'browser\', \'module\', \'main\'] // 这是默认行为
  }
};
```

因此，在排查复杂的模块解析问题时，除了检查 `package.json`，还应该留意项目中的构建配置文件，确认是否存在自定义的解析规则。

下面我给你提供了一些具体的案例分析
# 1 案例1
scripts/moduleCG/cg-enhanced/lina_mono-biz_hotspot-crystal-dytrending_related_movie_v2.json

```json
"@byted-crystal/dytrending-related-movie-v2@3.1.0:src/components/index/index.ts:80:33:<anonymous>": [
      {
        "api": "<@byted-lina/morphling-bridge>.open()",
        "importType": "import",
        "matched_module": [
          {
            "moduleName": "@bridge/search_hybrid",
            "modulePath": "/Users/bytedance/File/chayihua/lina-mono/node_modules/.pnpm/@bridge+search_hybrid@3.1.14/node_modules/@bridge/search_hybrid",
            "matched_functions": [
              "@bridge/search_hybrid@3.1.14:lib/search_hybrid.development.js:4991:2:open",
              "@bridge/search_hybrid@3.1.14:lib/search_hybrid.es.js:4983:1:open",
              "@bridge/search_hybrid@3.1.14:lib/search_hybrid.lynx.js:1210:1:open",
              "@bridge/search_hybrid@3.1.14:src/lynx/open.ts:35:1:open",
              "@bridge/search_hybrid@3.1.14:src/web/open.ts:35:1:open"
            ]
          }
        ]
      },
```

scripts/moduleCG/tp_config/lina_mono-node_modules-.pnpm-@bridge+search_hybrid@3.1.14-node_modules-@bridge-search_hybrid.json

```json
{
  "name": "@bridge/search_hybrid",
  "version": "3.1.14",
  "main": "lib/search_hybrid.js",
  "module": "lib/search_hybrid.es.js",
  "lynx": "lib/search_hybrid.lynx.js",
  "react-native": "lib/search_hybrid.native.js",
  "types": "lib/web/index.d.ts",
  "author": "juchangrong@bytedance.com",
  "license": "ISC",
  "unpkg": true,
  "files": [
    "dist",
    "lib",
    "src"
  ],
  "dependencies": {
    "@bridge/bytedance": "2.3.9"
  },
  "sideEffects": false
}
```

没有export，有lynx看lynx，根据"lynx": "lib/search_hybrid.lynx.js",确定唯一最优"@bridge/search_hybrid@3.1.14:lib/search_hybrid.lynx.js:1210:1:open",

# 2 案例2
scripts/moduleCG/cg-enhanced/lina_mono-biz_hotspot-morphling-douyin_hotspot_share_page.json

```json
{
        "api": "<@byted-lina/lepus-utils/dist/douyin/huodong>.getModuleStyle()",
        "importType": "import",
        "matched_module": [
          {
            "moduleName": "@byted-lina/lepus-utils",
            "modulePath": "/Users/bytedance/File/chayihua/lina-mono/packages/lina/lina-lepus-utils",
            "matched_functions": [
              "@byted-lina/lepus-utils@21.1.0:src/douyin/combine-card-group-style.ts:27:8:getModuleStyle",
              "@byted-lina/lepus-utils@21.1.0:src/douyin/huodong.ts:54:8:getModuleStyle"
            ]
          }
        ]
      }
```

lina-mono/packages/lina/lina-lepus-utils/package.json

```json
{
  "name": "@byted-lina/lepus-utils",
  "version": "21.1.0",
  "description": "Project created by Eden",
  "keywords": ["lepus", "utils"],
  "license": "ISC",
  "maintainers": ["yanhongwei", "gouwantong", "lihongxun", "wangjian.xiaofan", "wangchenghao.chester", "zhusichao"],
  "sideEffects": false,
  "main": "dist/index.js",
  "module": "dist/index.js",
  "types": "dist/index.d.js",
  "files": ["dist", "docs"],
  "scripts": {
    "build": "rm -rf dist && ttsc",
    "build:doc": "typedoc",
    "prepublish:only": "typedoc",
    "start": "ttsc -w",
    "test": "jest",
    "test:type": "ttsc --noemit"
  },
  "dependencies": {
    "@byted-lina/morphling-types": "workspace:*"
  },
  "devDependencies": {
    "@byted-lina/shared-configs": "workspace:*",
    "@byted-lina/types": "workspace:*",
    "@types/jest": "^27.0.1",
    "jest": "^27.4.5",
    "ts-jest": "^27.1.2",
    "ts-node": "^10.5.0",
    "ttypescript": "^1.5.15",
    "typedoc": "^0.25.4",
    "typedoc-plugin-markdown": "^3.17.1",
    "typescript": "^4.5.2"
  }
}
```

首先没有export，没有lynx 因为"importTpe": "import",所以优先考虑module "module": "dist/index.js",同时观察到目标api "<@byted-lina/lepus-utils/dist/douyin/huodong>.getModuleStyle()",含有相对路径，所以筛选路径上最高度匹配的"@byted-lina/lepus-utils@21.1.0:src/douyin/huodong.ts:54:8:getModuleStyle"

# 3 案例3
scripts/moduleCG/cg-enhanced/lina_mono-biz_activity-crystal-dyhuodong_ecom_more_tab_shop_aggregate.json

```json
{
        "api": "<@byted-lina/utils/dist/douyin/bcm>.createBtmChain()",
        "importType": "import",
        "matched_module": [
          {
            "moduleName": "@byted-lina/utils",
            "modulePath": "/Users/bytedance/File/chayihua/lina-mono/packages/lina/lina-utils",
            "matched_functions": [
              "@byted-lina/utils@24.1.0:src/douyin/bcm.ts:50:8:createBtmChain",
              "@byted-lina/utils@24.1.0:src/douyin/poi-search-bcm.ts:33:8:createBtmChain"
            ]
          }
        ]
      },
```

lina-mono/packages/lina/lina-utils/package.json

```json
{
  "name": "@byted-lina/utils",
  "version": "24.1.0",
  "description": "Project created by Eden",
  "keywords": ["lina", "utils"],
  "license": "ISC",
  "maintainers": ["yanhongwei", "zhusichao"],
  "main": "dist/index.js",
  "module": "dist/index.js",
  "types": "dist/index.d.ts",
  "files": ["dist", "docs"],
  "scripts": {
    "build": "rm -rf dist && tsc",
    "build:doc": "typedoc",
    "prepublish:only": "typedoc",
    "start": "tsc -w",
    "test": "TZ=Asia/Shanghai jest",
    "test:type": "tsc --noemit"
  },
  "dependencies": {
    "@byted-btm/hybrid": "1.2.4",
    "@byted-growth/zlink-sdk-lynx": "1.2.4",
    "@byted-life/confirm-order-direct-show": "0.1.7",
    "@byted-lina/lina-mixin-entity": "workspace:*",
    "@byted-lina/morphling-bridge": "workspace:*",
    "@byted-lina/tracker": "workspace:*",
    "@byted-poi/biz": "^4.1.14",
    "@byted-poi/btm-sdk": "2.1.3",
    "@byted/tma_schema_codec": "^4.0.2"
  },
  "devDependencies": {
    "@bridge/life": "latest",
    "@byted-lina/morphling-types": "workspace:*",
    "@byted-lina/shared-configs": "workspace:*",
    "@byted-lina/types": "workspace:*",
    "@byted-poi/tracker": "latest",
    "@types/jest": "^27.0.1",
    "jest": "^27.4.5",
    "ts-jest": "^27.1.2",
    "typedoc": "^0.25.4",
    "typedoc-plugin-markdown": "^3.17.1",
    "typescript": "^4.8.2",
    "url": "^0.11.0"
  }
}
```

首先没有export，没有lynx 因为"importTpe": "import",所以优先考虑module "module": "dist/index.js",，观察到api中含有"<@byted-lina/utils/dist/douyin/bcm>.createBtmChain()"，选择路径最匹配的 "@byted-lina/utils@24.1.0:src/douyin/bcm.ts:50:8:createBtmChain",

# 4 案例4
scripts/moduleCG/cg-enhanced/lina_mono-biz_activity-crystal-dyhuodong_ecom_gov_cat_qual.json

```json
{
        "api": "<@ecom/gov-subsidy-sdk>.applySDK.init()",
        "importType": "import",
        "matched_module": [
          {
            "moduleName": "@ecom/gov-subsidy-sdk",
            "modulePath": "/Users/bytedance/File/chayihua/lina-mono/node_modules/.pnpm/@ecom+gov-subsidy-sdk@0.1.2_@byted-lynx+react@0.23.2_@byted-lynx+lynx-speedy@3.6.3_@byted-lyn_hktwnmsxa7tjkvjohcmvakreky/node_modules/@ecom/gov-subsidy-sdk",
            "matched_functions": [
              "@ecom/gov-subsidy-sdk@0.1.2:dist/es/index.js:231:3:init",
              "@ecom/gov-subsidy-sdk@0.1.2:dist/lib/index.js:256:3:init",
              "@ecom/gov-subsidy-sdk@0.1.2:src/apply-sdk/index.ts:26:3:init"
            ]
          }
        ]
      },
```

lina-mono/node_modules/.pnpm/@ecom+gov-subsidy-sdk@0.1.2_@byted-lynx+react@0.23.2_@byted-lynx+lynx-speedy@3.6.3_@byted-lyn_hktwnmsxa7tjkvjohcmvakreky/node_modules/@ecom/gov-subsidy-sdk/package.json

```json
{
  "name": "@ecom/gov-subsidy-sdk",
  "version": "0.1.2",
  "types": "./dist/types/index.d.ts",
  "jsnext:source": "./src/index.ts",
  "main": "./dist/lib/index.js",
  "module": "./dist/es/index.js",
  "dependencies": {
    "@byted/remew-bridge": "1.28.11",
    "@ecom/dayan-log-js": "0.0.15"
  },
  "devDependencies": {
    "@byted/eslint-config-standard": "^3.1.1",
    "@byted/eslint-config-standard-react": "^2.1.1",
    "@byted/eslint-config-standard-ts": "^3.1.1",
    "@edenx/module-tools": "1.67.3",
    "eslint-plugin-prettier": "~5.2.2",
    "prettier": "^3.4.2",
    "rimraf": "~3.0.2",
    "typescript": "~5.0.4"
  },
  "publishConfig": {
    "access": "public",
    "registry": "https://bnpm.byted.org/"
  },
  "scripts": {
    "dev": "edenx-module dev",
    "build": "edenx-module build",
    "build:watch": "edenx-module build -w",
    "new": "edenx-module new",
    "upgrade": "edenx-module upgrade"
  }
}
```

首先没有export，没有lynx 因为"importTpe": "import",所以优先考虑module "module": "./dist/es/index.js", 所以选择带有es的"@ecom/gov-subsidy-sdk@0.1.2:dist/es/index.js:231:3:init",

# 5 案例5:
scripts/moduleCG/cg-enhanced/lina_mono-apps-websites-morphling_design_website.json

```json
"morphling-design-website@0.0.0:scripts/updateIconDoc.js": [
      {
        "api": "<@byted-lynx/parser-ttml>.parse()",
        "importType": "require",
        "matched_module": [
          {
            "moduleName": "@byted-lynx/parser-ttml",
            "modulePath": "/Users/bytedance/File/chayihua/lina-mono/node_modules/.pnpm/@byted-lynx+parser-ttml@2.18.2/node_modules/@byted-lynx/parser-ttml",
            "matched_functions": [
              "@byted-lynx/parser-ttml@2.18.2:cjs/lynx/index.js:74:1:parse",
              "@byted-lynx/parser-ttml@2.18.2:cjs/parser/parser.js:332:5:parse",
              "@byted-lynx/parser-ttml@2.18.2:cjs/parser/parser.js:661:1:parse",
              "@byted-lynx/parser-ttml@2.18.2:esm/lynx/index.js:33:8:parse",
              "@byted-lynx/parser-ttml@2.18.2:esm/parser/parser.js:295:5:parse",
              "@byted-lynx/parser-ttml@2.18.2:esm/parser/parser.js:624:8:parse"
            ]
          }
        ]
      }
```

/Users/bytedance/File/chayihua/lina-mono/node_modules/.pnpm/@byted-lynx+parser-ttml@2.18.2/node_modules/@byted-lynx/parser-ttml/package.json

```json
{
  "name": "@byted-lynx/parser-ttml",
  "version": "2.18.2",
  "description": "ttml AST builder",
  "license": "MIT",
  "type": "module",
  "exports": {
    ".": {
      "import": {
        "types": "./esm/index.d.ts",
        "default": "./esm/index.js"
      },
      "require": {
        "types": "./cjs/index.d.ts",
        "default": "./cjs/index.js"
      }
    }
  },
  "source": "./src/index.ts",
  "types": "./esm/index.d.ts",
  "files": [
    "cjs",
    "!cjs/**/*.js.map",
    "esm",
    "!esm/**/*.js.map",
    "README.md",
    "CHANGELOG.md",
    "package.json"
  ],
  "dependencies": {
    "@byted-lynx/parser-syntax": "2.3.5",
    "source-map": "^0.7.4",
    "@byted-lynx/parser-utils": "1.5.4"
  },
  "devDependencies": {
    "@types/fs-extra": "11.0.4",
    "@types/node": "^20.17.30",
    "glob": "^11.0.1",
    "rimraf": "^6.0.1",
    "yaml": "2.7.1"
  },
  "engines": {
    "node": ">=14.13.1"
  },
  "scripts": {
    "test": "vitest",
    "test:update": "vitest -u"
  }
}
```

观察到有export，那么按照export来，看到importType是require 所以按照     
 "require": {
        "types": "./cjs/index.d.ts",
        "default": "./cjs/index.js"
      }
所以选择最匹配的"@byted-lynx/parser-ttml@2.18.2:cjs/lynx/index.js:74:1:parse",

# 案例6

**API 调用**

```json
"@byted-morphling/26-ershouche@1.0.0:src/pages/index/process.lepus.js:5:1:processRawData": [
      {
        "api": "<@byted-lina/lepus-utils/dist/lego>.getToutiaoProps()",
        "importType": "import",
        "matched_module": [
          {
            "moduleName": "@byted-lina/lepus-utils",
            "modulePath": "/Users/bytedance/File/chayihua/lina-mono/packages/lina/lina-lepus-utils",
            "matched_functions": [
              "@byted-lina/lepus-utils@21.1.0:src/lego/getToutiaoProps.ts:7:8:getToutiaoProps",
              "@byted-lina/lepus-utils@21.1.0:src/lego/toutiao.ts:180:8:getToutiaoProps"
            ]
          }
        ]
      }
    ]
```

**package.json 配置**

```json
{
  "name": "@byted-lina/lepus-utils",
  "version": "21.1.0",
  "description": "Project created by Eden",
  "keywords": ["lepus", "utils"],
  "license": "ISC",
  "maintainers": ["yanhongwei", "gouwantong", "lihongxun", "wangjian.xiaofan", "wangchenghao.chester", "zhusichao"],
  "sideEffects": false,
  "main": "dist/index.js",
  "module": "dist/index.js",
  "types": "dist/index.d.js",
  "files": ["dist", "docs"],
  "scripts": {
    "build": "rm -rf dist && ttsc",
    "build:doc": "typedoc",
    "prepublish:only": "typedoc",
    "start": "ttsc -w",
    "test": "jest",
    "test:type": "ttsc --noemit"
  },
  "dependencies": {
    "@byted-lina/morphling-types": "workspace:*"
  },
  "devDependencies": {
    "@byted-lina/shared-configs": "workspace:*",
    "@byted-lina/types": "workspace:*",
    "@types/jest": "^27.0.1",
    "jest": "^27.4.5",
    "ts-jest": "^27.1.2",
    "ts-node": "^10.5.0",
    "ttypescript": "^1.5.15",
    "typedoc": "^0.25.4",
    "typedoc-plugin-markdown": "^3.17.1",
    "typescript": "^4.5.2"
  }
}
```

**推理过程**：  
根据知识库中的模块解析规则，首先检查 `package.json` 是否存在 `exports` 字段。此处没有 `exports` 字段，因此进入传统回退机制。由于运行环境为 Lynx，检查是否存在 `lynx` 字段，但 `package.json` 中没有 `lynx` 字段。接着，观察到 `importType` 为 `"import"`，表示使用 ESM 导入方式，因此优先考虑 `module` 字段。`module` 字段指向 `"dist/index.js"`，但该路径仅为入口文件，未提供具体子路径信息。API 调用为 `<@byted-lina/lepus-utils/dist/lego>.getToutiaoProps()`，其中包含子路径 `dist/lego`，表明需要匹配与 `lego` 相关的实现。候选函数包括：  
- `"@byted-lina/lepus-utils@21.1.0:src/lego/getToutiaoProps.ts:7:8:getToutiaoProps"`  
- `"@byted-lina/lepus-utils@21.1.0:src/lego/toutiao.ts:180:8:getToutiaoProps"`  

两个候选函数的路径均包含 `src/lego`，与 API 调用的 `dist/lego` 路径在语义上相关，但由于 `module` 字段仅指向 `dist/index.js`，且没有更具体的子路径映射，两个函数的路径匹配度相当，无法进一步确定具体实现。因此，保留两个候选函数作为可能的结果：  
- `"@byted-lina/lepus-utils@21.1.0:src/lego/getToutiaoProps.ts:7:8:getToutiaoProps"`  
- `"@byted-lina/lepus-utils@21.1.0:src/lego/toutiao.ts:180:8:getToutiaoProps"`

# 案例7

**API 调用**

```json
"@byted-lina/hotspot-lepus-utils@29.0.0:scripts/transformer.ts:3:70:<anonymous>": [
      {
        "api": "<typescript>.visitNode()",
        "importType": "import",
        "matched_module": [
          {
            "moduleName": "typescript",
            "modulePath": "/Users/bytedance/File/chayihua/lina-mono/node_modules/.pnpm/typescript@4.9.5/node_modules/typescript",
            "matched_functions": [
              "typescript@4.9.5:lib/tsc.js:25132:5:visitNode",
              "typescript@4.9.5:lib/tsc.js:31888:13:visitNode",
              "typescript@4.9.5:lib/tsc.js:31962:13:visitNode",
              "typescript@4.9.5:lib/tsc.js:32105:17:visitNode",
              "typescript@4.9.5:lib/tsc.js:76994:5:visitNode",
              "typescript@4.9.5:lib/tsserver.js:31214:5:visitNode",
              "typescript@4.9.5:lib/tsserver.js:39320:13:visitNode",
              "typescript@4.9.5:lib/tsserver.js:39448:13:visitNode",
              "typescript@4.9.5:lib/tsserver.js:39669:17:visitNode",
              "typescript@4.9.5:lib/tsserver.js:91320:5:visitNode",
              "typescript@4.9.5:lib/tsserverlibrary.js:31213:5:visitNode",
              "typescript@4.9.5:lib/tsserverlibrary.js:39319:13:visitNode",
              "typescript@4.9.5:lib/tsserverlibrary.js:39447:13:visitNode",
              "typescript@4.9.5:lib/tsserverlibrary.js:39668:17:visitNode",
              "typescript@4.9.5:lib/tsserverlibrary.js:91319:5:visitNode",
              "typescript@4.9.5:lib/typescript.js:31204:5:visitNode",
              "typescript@4.9.5:lib/typescript.js:39310:13:visitNode",
              "typescript@4.9.5:lib/typescript.js:39438:13:visitNode",
              "typescript@4.9.5:lib/typescript.js:39659:17:visitNode",
              "typescript@4.9.5:lib/typescript.js:91310:5:visitNode",
              "typescript@4.9.5:lib/typescriptServices.js:31204:5:visitNode",
              "typescript@4.9.5:lib/typescriptServices.js:39310:13:visitNode",
              "typescript@4.9.5:lib/typescriptServices.js:39438:13:visitNode",
              "typescript@4.9.5:lib/typescriptServices.js:39659:17:visitNode",
              "typescript@4.9.5:lib/typescriptServices.js:91310:5:visitNode",
              "typescript@4.9.5:lib/typingsInstaller.js:31194:5:visitNode",
              "typescript@4.4.9.5:lib/typingsInstaller.js:39300:13:visitNode",
              "typescript@4.9.5:lib/typingsInstaller.js:39428:13:visitNode",
              "typescript@4.9.5:lib/typingsInstaller.js:39649:17:visitNode",
              "typescript@4.9.5:lib/typingsInstaller.js:91300:5:visitNode"
            ]
          }
        ]
      }
    ]
```

**package.json 配置**

```json
{
    "name": "typescript",
    "author": "Microsoft Corp.",
    "homepage": "https://www.typescriptlang.org/",
    "version": "4.9.5",
    "license": "Apache-2.0",
    "description": "TypeScript is a language for application scale JavaScript development",
    "keywords": [
        "TypeScript",
        "Microsoft",
        "compiler",
        "language",
        "javascript"
    ],
    "bugs": {
        "url": "https://github.com/Microsoft/TypeScript/issues"
    },
    "repository": {
        "type": "git",
        "url": "https://github.com/Microsoft/TypeScript.git"
    },
    "main": "./lib/typescript.js",
    "typings": "./lib/typescript.d.ts",
    "bin": {
        "tsc": "./bin/tsc",
        "tsserver": "./bin/tsserver"
    },
    "engines": {
        "node": ">=4.2.0"
    },
    "files": [
        "bin",
        "lib",
        "!lib/enu",
        "LICENSE.txt",
        "README.md",
        "SECURITY.md",
        "ThirdPartyNoticeText.txt",
        "!**/.gitattributes"
    ],
    "devDependencies": {
        // 省略
    },
    "overrides": {
        "es5-ext": "0.10.53"
    },
    "scripts": {
        "test": "gulp runtests-parallel --light=false",
        "test:eslint-rules": "gulp run-eslint-rules-tests",
        "build": "npm run build:compiler && npm run build:tests",
        "build:compiler": "gulp local",
        "build:tests": "gulp tests",
        "start": "node lib/tsc",
        "clean": "gulp clean",
        "gulp": "gulp",
        "lint": "gulp lint",
        "setup-hooks": "node scripts/link-hooks.mjs"
    },
    "browser": {
        "fs": false,
        "os": false,
        "path": false,
        "crypto": false,
        "buffer": false,
        "@microsoft/typescript-etw": false,
        "source-map-support": false,
        "inspector": false
    },
    "packageManager": "npm@8.15.0",
    "volta": {
        "node": "14.20.0",
        "npm": "8.15.0"
    }
}
```

**推理过程**：  
根据知识库中的模块解析规则，首先检查 `package.json` 是否存在 `exports` 字段。此处没有 `exports` 字段，因此进入传统回退机制。由于运行环境未明确指定为 Lynx 或其他平台，且 `package.json` 中存在 `browser` 字段，但该字段仅用于屏蔽 Node.js 特定模块（如 `fs`），与当前 API 无关。`importType` 为 `"import"`，表示使用 ESM 导入方式，现代构建工具通常优先考虑 `module` 字段，但此处 `package.json` 未定义 `module` 字段，因此回退到 `main` 字段。`main` 字段指向 `"./lib/typescript.js"`，表明这是默认入口文件。API 调用为 `<typescript>.visitNode()`，未指定子路径，仅指向模块根路径的 `visitNode` 方法。候选函数中，包含 `lib/typescript.js` 的实现有：  
- `"typescript@4.9.5:lib/typescript.js:31204:5:visitNode"`  
- `"typescript@4.9.5:lib/typescript.js:39310:13:visitNode"`  
- `"typescript@4.9.5:lib/typescript.js:39438:13:visitNode"`  
- `"typescript@4.9.5:lib/typescript.js:39659:17:visitNode"`  
- `"typescript@4.9.5:lib/typescript.js:91310:5:visitNode"`  

由于 `main` 字段明确指向 `lib/typescript.js`，且 API 调用未提供更具体的子路径信息，无法进一步区分这些函数的具体实现，因此所有来自 `lib/typescript.js` 的 `visitNode` 函数均可能匹配，保留以下结果：  
- `"typescript@4.9.5:lib/typescript.js:31204:5:visitNode"`  
- `"typescript@4.9.5:lib/typescript.js:39310:13:visitNode"`  
- `"typescript@4.9.5:lib/typescript.js:39438:13:visitNode"`  
- `"typescript@4.9.5:lib/typescript.js:39659:17:visitNode"`  
- `"typescript@4.9.5:lib/typescript.js:91310:5:visitNode"`
