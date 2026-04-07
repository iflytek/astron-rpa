import i18next, { type Resource } from "i18next";
import LanguageDetector from "i18next-browser-languagedetector";
import I18NextVue from "i18next-vue";
import { get, hasIn, isEmpty, isObject, isString, template } from "lodash-es";
import deepmerge from "deepmerge";
import enUS from "@rpa/locales/en-US.json";
import zhCN from "@rpa/locales/zh-CN.json";

export { useTranslation } from "i18next-vue";
export { TranslationComponent } from "i18next-vue";

type ResourceKey = {
  [key: string]: any;
};

export type LanguageType = "zh-CN" | "en-US";

export const LanguageText: Record<LanguageType, string> = {
  "zh-CN": "简体中文",
  "en-US": "English",
};

export type LanguageResource = Record<LanguageType, ResourceKey>;

function isI18n(str: unknown): str is LanguageType {
  return isObject(str) && hasIn(str, "zh-CN") && hasIn(str, "en-US");
}

function translate(
  str: string | LanguageType,
  variables?: Record<string, string>,
): string {
  if (isString(str)) return str;

  if (isI18n(str)) {
    const text = get(str, i18next.language);

    if (isEmpty(variables)) return text;

    const compiled = template(text, { interpolate: /\{\{([\s\S]+?)\}\}/g });
    return compiled(variables);
  }

  return "";
}

export function initI18next(_resources?: LanguageResource) {
  const locale_resources: LanguageResource = {
    "zh-CN": zhCN,
    "en-US": enUS,
  };

  const resources = (Object.keys(locale_resources) as LanguageType[]).reduce(
    (acc, lng) => {
      acc[lng] = {
        translation: deepmerge<ResourceKey>(
          locale_resources[lng],
          _resources?.[lng] || {},
        ),
      };
      return acc;
    },
    {} as Resource,
  );

  i18next.use(LanguageDetector).init({
    debug: false,
    fallbackLng: "zh-CN",
    supportedLngs: Object.keys(resources),
    resources,
    interpolation: {
      escapeValue: false,
    },
  });

  function install(app: any) {
    app.use(I18NextVue, { i18next });
  }

  return Object.assign(i18next, { isI18n, translate, install });
}
