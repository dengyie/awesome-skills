/**
 * Allow/deny list resolution shared by domain and X-handle filters. Config is written by
 * the user, CLI args by the calling agent, so CLI values may narrow a configured list but
 * never widen it.
 */
import { ConfigError } from "./config.js";

function dedupeFilterValues(values) {
  const byKey = new Map();
  for (const value of values) {
    const key = value.toLowerCase();
    if (!byKey.has(key)) byKey.set(key, value);
  }
  return [...byKey.values()];
}

function containsValue(list, value) {
  return list.some((other) => other.toLowerCase() === value.toLowerCase());
}

/**
 * Resolve an allow/deny filter pair from CLI args over config.
 *
 * Config is written by the user, CLI args by the agent calling this tool, so a CLI
 * value must not silently discard a configured restriction. Both list kinds are
 * restrictions: a deny-list removes named values, an allow-list removes everything it
 * does not name. So command-line values may narrow either one but never widen it.
 *
 * - Configured allow-list: CLI allow values must be a subset of it; a CLI deny-list
 *   subtracts from it. Emptying it entirely is an error, because an empty allow-list
 *   means "no restriction" to the API — the opposite of what was configured.
 * - Configured deny-list: a CLI allow-list satisfies it vacuously unless it explicitly
 *   names an excluded value; two deny-lists are unioned rather than replaced.
 */
export function resolveFilterPair({
  argsAllowed,
  argsExcluded,
  configAllowed,
  configExcluded,
  allowedName,
  excludedName,
  max,
}) {
  const configAllowedList = configAllowed || [];
  const configExcludedList = configExcluded || [];
  if (argsAllowed == null && argsExcluded == null) {
    return { allowed: [...configAllowedList], excluded: [...configExcludedList] };
  }

  const allowed = argsAllowed == null ? [] : [...argsAllowed];
  const excluded = argsExcluded == null ? [] : [...argsExcluded];

  if (configAllowedList.length) {
    if (allowed.length) {
      const forbidden = allowed.filter((value) => !containsValue(configAllowedList, value));
      if (forbidden.length) {
        throw new ConfigError(
          `${allowedName} 请求了配置允许清单之外的值: ${forbidden.join(", ")}`,
          "RESPONSES_FILTER_FORBIDDEN"
        );
      }
      return { allowed, excluded: [] };
    }
    const narrowed = configAllowedList.filter((value) => !containsValue(excluded, value));
    if (!narrowed.length) {
      throw new ConfigError(
        `${excludedName} 排除了配置允许清单中的全部值，结果为空`,
        "RESPONSES_FILTER_EMPTY"
      );
    }
    return { allowed: narrowed, excluded: [] };
  }

  if (!configExcludedList.length) return { allowed, excluded };

  if (allowed.length) {
    const forbidden = allowed.filter((value) => containsValue(configExcludedList, value));
    if (forbidden.length) {
      throw new ConfigError(
        `${allowedName} 请求了配置中已排除的值: ${forbidden.join(", ")}`,
        "RESPONSES_FILTER_FORBIDDEN"
      );
    }
    return { allowed, excluded: [] };
  }

  const merged = dedupeFilterValues([...configExcludedList, ...excluded]);
  if (merged.length > max) {
    throw new ConfigError(
      `配置与命令行的排除项合并后超过 ${max} 个（${merged.length}）；请收敛其中一侧`,
      "RESPONSES_FILTER_LIMIT"
    );
  }
  return { allowed, excluded: merged };
}

export function validateExclusiveLists(left, right, leftName, rightName) {
  if (left.length && right.length) {
    throw new ConfigError(`${leftName} 与 ${rightName} 不能同时使用`, "RESPONSES_FILTER_CONFLICT");
  }
}

export function validateMaxItems(list, name, max) {
  if (list.length > max) throw new ConfigError(`${name} 最多支持 ${max} 个值`, "RESPONSES_FILTER_LIMIT");
}
