/*
 * Add direct source editing and issue-reporting links to the current page.
 * Unlike hosted Mintlify feedback, these links also work in local preview.
 */
(function () {
  "use strict";

  var repository = "https://github.com/necc-hub/docs";

  function targetsFor(rawPath) {
    var path = decodeURIComponent((rawPath || "/").split(/[?#]/)[0]);
    path = path.replace(/^\/+|\/+$/g, "") || "index";
    var sourcePath = path + ".mdx";
    var issueBody = [
      "页面：https://docs.newenergycoder.club/" + path,
      "源码：" + repository + "/blob/main/" + sourcePath,
      "",
      "## 发现的问题",
      "",
      "## 建议修改",
      "",
      "<!-- 请只描述公开文档问题，不要在此填写个人信息或密钥。 -->",
    ].join("\n");

    return {
      edit: repository + "/edit/main/" + sourcePath,
      issue: repository + "/issues/new?" + new URLSearchParams({
        title: "docs: " + path,
        labels: "documentation",
        body: issueBody,
      }).toString(),
    };
  }

  if (typeof module !== "undefined" && module.exports) {
    module.exports = { targetsFor: targetsFor };
  }

  if (typeof window === "undefined" || typeof document === "undefined") return;

  var lastNavigationPath = null;
  var lastNavigationViewport = null;

  function mountNavigation() {
    var isMobile = window.matchMedia("(max-width: 1023px)").matches;
    document.querySelectorAll("#navigation-items .sidebar-group-header[data-mobile-nav-toggle]").forEach(function (heading) {
      heading.style.display = isMobile ? "none" : "";
    });
    if (!isMobile) return;

    var pathChanged = lastNavigationPath !== window.location.pathname;
    lastNavigationPath = window.location.pathname;
    var viewportChanged = lastNavigationViewport !== isMobile;
    lastNavigationViewport = isMobile;
    document.querySelectorAll("#navigation-items .sidebar-group-header").forEach(function (heading) {
      var group = heading.parentElement;
      var pages = Array.from(group.children).find(function (child) {
        return child !== heading && child.matches("ul, div");
      });
      if (!pages || !pages.querySelector("a[href]")) return;

      var active = Boolean(group.querySelector('[aria-current="page"]'));
      var existing = group.querySelector(":scope > .mobile-nav-toggle");
      if (heading.getAttribute("data-mobile-nav-toggle") === "true") {
        if ((pathChanged || viewportChanged) && existing) {
          existing.setAttribute("aria-expanded", String(active));
          group.classList.toggle("mobile-nav-collapsed", !active);
        }
        return;
      }

      var title = heading.querySelector(".sidebar-title")?.textContent.trim();
      if (!title) return;
      var id = "mobile-nav-group-" + Array.from(document.querySelectorAll("#navigation-items .sidebar-group-header")).indexOf(heading);
      var toggle = document.createElement("button");
      toggle.type = "button";
      toggle.className = "mobile-nav-toggle";
      toggle.setAttribute("data-mobile-nav-toggle", "true");
      toggle.setAttribute("aria-controls", id);
      toggle.setAttribute("aria-expanded", String(active));
      toggle.textContent = title;
      var icon = document.createElement("span");
      icon.setAttribute("aria-hidden", "true");
      icon.textContent = "⌄";
      toggle.appendChild(icon);
      toggle.addEventListener("click", function () {
        var expanded = toggle.getAttribute("aria-expanded") === "true";
        toggle.setAttribute("aria-expanded", String(!expanded));
        group.classList.toggle("mobile-nav-collapsed", expanded);
      });

      heading.setAttribute("data-mobile-nav-toggle", "true");
      heading.setAttribute("aria-hidden", "true");
      heading.style.display = "none";
      pages.id = id;
      group.insertBefore(toggle, heading);
      group.classList.toggle("mobile-nav-collapsed", !active);
    });
  }

  function mount() {
    if (document.getElementById("page-maintenance-links")) return;
    var pagination = document.querySelector('main nav[aria-label="Pagination"]');
    var footer = document.querySelector("main > div > sectionfooter");
    var anchor = pagination || footer;
    if (!anchor || !anchor.parentNode) return;

    var targets = targetsFor(window.location.pathname);
    var container = document.createElement("div");
    container.id = "page-maintenance-links";
    container.className = "page-maintenance-links";

    var label = document.createElement("span");
    label.textContent = "参与维护";

    var edit = document.createElement("a");
    edit.href = targets.edit;
    edit.target = "_blank";
    edit.rel = "noopener noreferrer";
    edit.textContent = "编辑此页 ↗";

    var issue = document.createElement("a");
    issue.href = targets.issue;
    issue.target = "_blank";
    issue.rel = "noopener noreferrer";
    issue.textContent = "反馈问题 ↗";

    container.append(label, edit, issue);
    anchor.parentNode.insertBefore(container, anchor);
  }

  var scheduled = false;
  function scheduleMount() {
    if (scheduled) return;
    scheduled = true;
    window.requestAnimationFrame(function () {
      scheduled = false;
      mount();
      mountNavigation();
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mount, { once: true });
  } else {
    mount();
    mountNavigation();
  }
  new MutationObserver(scheduleMount).observe(document.body, {
    childList: true,
    subtree: true,
  });
})();
