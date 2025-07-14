/**
 * Copyright 2025 Beijing Volcano Engine Technology Co., Ltd. All Rights Reserved.
 * SPDX-license-identifier: BSD-3-Clause
 */

import { Provider } from '../basic';
import ArkSVG from '@/assets/img/Ark.svg';
import DeepSeekSVG from '@/assets/img/DeepSeek.svg';

export const ArkModel = {
  'Skylark-pro': {
    endPointId: 'ep-m-20250530010718-pmxzt',
    description: '128k, Trial supported',
    icon: ArkSVG,
  },
  'Skylark-lite': {
    endPointId: 'ep-20250603112522-swnmm',
    description: '32k, Trial supported',
    icon: ArkSVG,
  },
  'DeepSeek-R1｜250528': {
    endPointId: 'ep-20250603112606-rhnx6',
    description: '32k, Trial supported',
    icon: DeepSeekSVG,
  },
  'DeepSeek-R1｜250120': {
    endPointId: 'ep-20250603112754-sxwf6',
    description: '32k, Trial supported',
    icon: DeepSeekSVG,
  },
  'DeepSeek-V3｜250324': {
    endPointId: 'ep-20250603112638-tcsj2',
    description: '128k, Trial supported',
    icon: DeepSeekSVG,
  },
  'Deepseek-R1-Distill-Qwen-32b｜250120': {
    endPointId: 'ep-20250603112707-8qmlj',
    description: '32k, Trial supported',
    icon: DeepSeekSVG,
  },
};

export const OpenAiModel = {
  'GPT-4o': {
    endPointId: 'gpt-4o-2024-11-20',
    description: 'GPT-4o 2024-11-20',
  },
};

export const ModelMap = {
  [Provider.Byteplus]: ArkModel,
  [Provider.OpenAI]: OpenAiModel,
};

/**
 * @brief Flexible Mode (VoiceChat Mode) Config.
 * @note For more information, you can refer to https://docs.byteplus.com/en/docs/byteplus-rtc/docs-1316243
 *       Some sensitive fields not provided in frontend were injected by the server (See: Server/sensitive.js).
 */
export class LLMManager {
  provider: Provider.Byteplus | Provider.OpenAI;

  systemMessages: string[] = [];

  endPointId: string = ArkModel['Skylark-pro'].endPointId;

  #paramsMap: {
    [Provider.Byteplus]: {
      Mode: 'BytePlusArk';
      /**
       * @refer https://console.byteplus.com/voice/service/1000014?s=g
       */
      EndPointId: string;
      /**
       * @note Injected by server, refer to Server/sensitive.js.
       * @refer https://console.byteplus.com/ark/region:ark+ap-southeast-1/endpoint?s=g
       */
      APIKey?: string;
      Feature: string;
    };
    [Provider.OpenAI]: {
      Mode: 'CustomLLM';
      /**
       * @note Fixed value, `https://api.openai.com/v1/chat/completions`.
       */
      Url: 'changetoyour_3rdpartyurl-ensure-this-is-https-typically-i-use-ngrok/chat/stream';
      /**
       * @refer https://platform.openai.com/docs/models#tts
       */
      ModelName?: string;
      /**
       * @note Injected by server, refer to Server/sensitive.js.
       * @refer https://platform.openai.com/api-keys
       */
      APIKey?: string;
      SystemMessages?: string[];
      UserMessages?: string[];
      Feature: string;
    };
  };

  constructor() {
    this.provider = Provider.Byteplus;
    this.#paramsMap = {
      [Provider.Byteplus]: {
        Mode: 'BytePlusArk',
        EndPointId: ArkModel['Skylark-pro'].endPointId,
        Feature: JSON.stringify({ Http: true }),
      },
      [Provider.OpenAI]: {
        Url: 'changetoyour_3rdpartyurl-ensure-this-is-https-typically-i-use-ngrok/chat/stream',
        Mode: 'CustomLLM',
        ModelName: OpenAiModel['GPT-4o'].endPointId,
        SystemMessages: [],
        UserMessages: [],
        Feature: JSON.stringify({ Http: true }),
      },
    };
  }

  get value() {
    switch (this.provider) {
      case Provider.OpenAI:
        this.#paramsMap[this.provider].SystemMessages = this.systemMessages;
        this.#paramsMap[this.provider].ModelName = this.endPointId;
        break;
      case Provider.Byteplus:
        this.#paramsMap[this.provider].EndPointId = this.endPointId;
        break;
      default:
        break;
    }
    return this.#paramsMap[this.provider] || {};
  }
}