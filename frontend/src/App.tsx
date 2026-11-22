import { useState, useEffect, type FormEvent } from "react";
import "./App.css";

const API_URL = "http://localhost:8000/api";

interface AvailableTicketOption {
  ticket_id: number;
  barcode: string;
  sector_name: string;
  price: string | number;
}

interface AfishaItem {
  concert_id: number;
  artist: string;
  program_name: string;
  start_datetime: string;
  age_restriction: string | null;
  city: string;
  venue_name: string;
  price_from: string | number | null;
  available_tickets: AvailableTicketOption[];
}

interface CustomerTicket {
  ticket_id: number;
  barcode: string;
  artist: string;
  program_name: string;
  start_datetime: string;
  venue_name: string;
  sector_name: string;
  price: string | number;
  ticket_status: string;
}

interface SalesMonitoringItem {
  promoter: string;
  artist: string;
  program_name: string;
  venue_name: string;
  total_capacity: number;
  tickets_sold: number;
  occupancy_percent: number;
  total_revenue: string | number;
}

interface VenueConfigItem {
  venue_id: number;
  venue_name: string;
  city: string;
  total_capacity: number;
  sector_id: number;
  sector_name: string;
  sector_capacity: number;
  sector_type: string;
}

interface GateControlItem {
  concert_id: number;
  start_datetime: string;
  barcode: string;
  ticket_status: string;
  sector_name: string;
  sector_type: string;
  customer_full_name: string | null;
  phone_number: string | null;
}

interface ArtistPopularityItem {
  artist: string;
  music_genre: string | null;
  total_concerts: number;
  cities_visited: number;
  total_tickets_sold: number;
  total_gross: string | number;
}

interface AuditLogItem {
  log_item_id: number;
  operation_type: string | null;
  operation_date: string | null;
  user_operator: string | null;
  changed_data: string | null;
}

interface SecretDataItem {
  id: number;
  username: string | null;
  secret_token: string | null;
}

interface UserItem {
  login: string;
  roles: string[];
}

export default function App() {
  const [token, setToken] = useState<string>(localStorage.getItem("token") || "");
  const [currentLogin, setCurrentLogin] = useState<string>(
    localStorage.getItem("login") || ""
  );
  const [currentRoles, setCurrentRoles] = useState<string[]>(
    JSON.parse(localStorage.getItem("roles") || "[]")
  );

  const [isRegisterMode, setIsRegisterMode] = useState<boolean>(false);
  const [loginInput, setLoginInput] = useState<string>("");
  const [passwordInput, setPasswordInput] = useState<string>("");
  const [authError, setAuthError] = useState<string>("");
  const [authSuccess, setAuthSuccess] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [actionAlert, setActionAlert] = useState<{
    text: string;
    isError: boolean;
  } | null>(null);

  const [activeTab, setActiveTab] = useState<string>("afisha");

  const [afisha, setAfisha] = useState<AfishaItem[]>([]);
  const [selectedTickets, setSelectedTickets] = useState<Record<number, number>>({});
  const [cityFilter, setCityFilter] = useState<string>("");
  const [genreFilter, setGenreFilter] = useState<string>("");
  const [afishaSort, setAfishaSort] = useState<string>("date_asc");

  const [userTickets, setUserTickets] = useState<CustomerTicket[]>([]);

  const [salesList, setSalesList] = useState<SalesMonitoringItem[]>([]);
  const [promoterFilter, setPromoterFilter] = useState<string>("");
  const [venueFilter, setVenueFilter] = useState<string>("");
  const [salesSort, setSalesSort] = useState<string>("revenue_desc");

  const [venuesConfig, setVenuesConfig] = useState<VenueConfigItem[]>([]);
  const [programName, setProgramName] = useState<string>("");
  const [startDatetime, setStartDatetime] = useState<string>("2026-12-30T19:00");
  const [ageRestriction, setAgeRestriction] = useState<string>("16+");
  const [artistId, setArtistId] = useState<string>("1");
  const [venueId, setVenueId] = useState<string>("1");
  const [promoterId, setPromoterId] = useState<string>("1");

  const [relConcertId, setRelConcertId] = useState<string>("1");
  const [relSectorId, setRelSectorId] = useState<string>("1");
  const [relPrice, setRelPrice] = useState<string>("3500");
  const [relCount, setRelCount] = useState<string>("5");

  const [scanBarcodeInput, setScanBarcodeInput] = useState<string>("");
  const [scannedTicket, setScannedTicket] = useState<GateControlItem | null>(null);

  const [popularityList, setPopularityList] = useState<ArtistPopularityItem[]>([]);
  const [popGenreFilter, setPopGenreFilter] = useState<string>("");
  const [popSort, setPopSort] = useState<string>("gross_desc");

  const [tablesList, setTablesList] = useState<string[]>([]);
  const [selectedTable, setSelectedTable] = useState<string>("");
  const [tableRows, setTableRows] = useState<Record<string, string | number | null>[]>([]);
  const [tableSearch, setTableSearch] = useState<string>("");

  const [auditLogs, setAuditLogs] = useState<AuditLogItem[]>([]);
  const [auditOpFilter, setAuditOpFilter] = useState<string>("");

  const [secretData, setSecretData] = useState<SecretDataItem[]>([]);
  const [usersList, setUsersList] = useState<UserItem[]>([]);

  const isStaff =
    currentRoles.includes("staff_group_role") ||
    currentRoles.includes("admin_group_role");
  const isAdmin = currentRoles.includes("admin_group_role");

  const showAlert = (text: string, isError: boolean) => {
    setActionAlert({ text, isError });
    setTimeout(() => setActionAlert(null), 4000);
  };

  useEffect(() => {
    if (!token) return;
    if (activeTab === "afisha") fetchAfisha();
    if (activeTab === "tickets") fetchUserTickets();
    if (activeTab === "sales" && isStaff) fetchSalesMonitoring();
    if (activeTab === "venues" && isStaff) fetchVenuesConfig();
    if (activeTab === "popularity" && isAdmin) fetchArtistPopularity();
    if (activeTab === "tables" && isAdmin) fetchTablesList();
    if (activeTab === "audit" && isAdmin) fetchAuditLogs();
    if (activeTab === "secrets" && isAdmin) fetchSecretData();
    if (activeTab === "roles" && isAdmin) fetchUsers();
  }, [token, activeTab]);

  const handleAuthSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (loading) return;
    setLoading(true);
    setAuthError("");
    setAuthSuccess("");

    const endpoint = isRegisterMode ? "/register" : "/login";

    try {
      const response = await fetch(`${API_URL}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ login: loginInput, password: passwordInput }),
      });
      const data = await response.json();

      if (!response.ok) {
        setAuthError(data.detail || "Ошибка авторизации");
        return;
      }

      setAuthSuccess(data.message);
      setToken(data.access_token);
      setCurrentLogin(data.login);
      setCurrentRoles(data.roles);
      setActiveTab("afisha");

      localStorage.setItem("token", data.access_token);
      localStorage.setItem("login", data.login);
      localStorage.setItem("roles", JSON.stringify(data.roles));
    } catch {
      setAuthError("Ошибка соединения с сервером");
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    setToken("");
    setCurrentLogin("");
    setCurrentRoles([]);
    localStorage.clear();
  };

  const fetchAfisha = async () => {
    const params = new URLSearchParams();
    if (cityFilter.trim()) params.append("city", cityFilter.trim());
    if (genreFilter.trim()) params.append("genre", genreFilter.trim());

    try {
      const response = await fetch(`${API_URL}/afisha?${params.toString()}`, {
        headers: { token },
      });
      const data = await response.json();
      if (response.ok) {
        setAfisha(data.items);
      }
    } catch {
      showAlert("Ошибка загрузки афиши", true);
    }
  };

  const fetchUserTickets = async () => {
    try {
      const response = await fetch(`${API_URL}/tickets/user`, {
        headers: { token },
      });
      const data = await response.json();
      if (response.ok) {
        setUserTickets(data.tickets);
      }
    } catch {
      showAlert("Ошибка загрузки билетов", true);
    }
  };

  const handleBuyConcertTicket = async (concert: AfishaItem) => {
    if (concert.available_tickets.length === 0 || loading) return;
    const ticketId =
      selectedTickets[concert.concert_id] ??
      concert.available_tickets[0].ticket_id;

    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/tickets/buy`, {
        method: "POST",
        headers: { "Content-Type": "application/json", token },
        body: JSON.stringify({ ticket_id: ticketId }),
      });
      const data = await response.json();
      if (!response.ok) {
        showAlert(data.detail || "Не удалось купить билет", true);
        return;
      }
      showAlert(
        `Билет куплен: ${data.ticket.sector_name} (штрихкод ${data.ticket.barcode})`,
        false
      );
      setSelectedTickets((prev) => {
        const next = { ...prev };
        delete next[concert.concert_id];
        return next;
      });
      fetchAfisha();
    } catch {
      showAlert("Ошибка покупки билета", true);
    } finally {
      setLoading(false);
    }
  };

  const handleRefundTicket = async (ticketId: number) => {
    if (loading) return;
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/tickets/${ticketId}/refund`, {
        method: "POST",
        headers: { token },
      });
      const data = await response.json();
      if (!response.ok) {
        showAlert(data.detail || "Ошибка возврата", true);
        return;
      }
      showAlert("Билет возвращен", false);
      fetchUserTickets();
    } catch {
      showAlert("Ошибка возврата", true);
    } finally {
      setLoading(false);
    }
  };

  const fetchSalesMonitoring = async () => {
    const params = new URLSearchParams();
    if (promoterFilter.trim()) params.append("promoter_name", promoterFilter.trim());
    if (venueFilter.trim()) params.append("venue_name", venueFilter.trim());

    try {
      const response = await fetch(
        `${API_URL}/staff/sales-monitoring?${params.toString()}`,
        { headers: { token } }
      );
      const data = await response.json();
      if (response.ok) {
        setSalesList(data.items);
      } else {
        showAlert(data.detail || "Доступ запрещен", true);
      }
    } catch {
      showAlert("Ошибка загрузки мониторинга продаж", true);
    }
  };

  const fetchVenuesConfig = async () => {
    try {
      const response = await fetch(`${API_URL}/staff/venues-config`, {
        headers: { token },
      });
      const data = await response.json();
      if (response.ok) {
        setVenuesConfig(data.items);
      }
    } catch {
      showAlert("Ошибка загрузки площадок", true);
    }
  };

  const handleCreateConcert = async (e: FormEvent) => {
    e.preventDefault();
    if (loading) return;
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/staff/concerts`, {
        method: "POST",
        headers: { "Content-Type": "application/json", token },
        body: JSON.stringify({
          program_name: programName,
          start_datetime: startDatetime,
          age_restriction: ageRestriction,
          artist_id: Number(artistId),
          venue_id: Number(venueId),
          promoter_id: Number(promoterId),
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        showAlert(data.detail || "Ошибка создания концерта", true);
        return;
      }
      showAlert(`Концерт создан (ID: ${data.concert_id})`, false);
      setProgramName("");
    } catch {
      showAlert("Ошибка создания концерта", true);
    } finally {
      setLoading(false);
    }
  };

  const handleReleaseTickets = async (e: FormEvent) => {
    e.preventDefault();
    if (loading) return;
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/staff/tickets/release`, {
        method: "POST",
        headers: { "Content-Type": "application/json", token },
        body: JSON.stringify({
          concert_id: Number(relConcertId),
          sector_id: Number(relSectorId),
          price: Number(relPrice),
          count: Number(relCount),
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        showAlert(data.detail || "Превышена вместимость сектора", true);
        return;
      }
      showAlert(`Выпущено билетов: ${data.barcodes.length}`, false);
    } catch {
      showAlert("Ошибка выпуска билетов", true);
    } finally {
      setLoading(false);
    }
  };

  const handleScanTicket = async (e: FormEvent) => {
    e.preventDefault();
    if (!scanBarcodeInput.trim() || loading) return;
    setLoading(true);
    setScannedTicket(null);
    try {
      const response = await fetch(`${API_URL}/staff/gate-control`, {
        method: "POST",
        headers: { "Content-Type": "application/json", token },
        body: JSON.stringify({ barcode: scanBarcodeInput.trim() }),
      });
      const data = await response.json();
      if (!response.ok) {
        showAlert(data.detail || "Билет не найден", true);
        return;
      }
      setScannedTicket(data.item);
    } catch {
      showAlert("Ошибка проверки штрихкода", true);
    } finally {
      setLoading(false);
    }
  };

  const fetchArtistPopularity = async () => {
    const params = new URLSearchParams();
    if (popGenreFilter.trim()) params.append("genre", popGenreFilter.trim());
    try {
      const response = await fetch(
        `${API_URL}/admin/artist-popularity?${params.toString()}`,
        { headers: { token } }
      );
      const data = await response.json();
      if (response.ok) {
        setPopularityList(data.items);
      }
    } catch {
      showAlert("Ошибка загрузки статистики артистов", true);
    }
  };

  const fetchTablesList = async () => {
    try {
      const response = await fetch(`${API_URL}/admin/tables`, {
        headers: { token },
      });
      const data = await response.json();
      if (response.ok) {
        setTablesList(data.tables);
        if (data.tables.length > 0 && !selectedTable) {
          fetchTableData(data.tables[0]);
        }
      }
    } catch {
      showAlert("Ошибка получения списка таблиц", true);
    }
  };

  const fetchTableData = async (tableName: string) => {
    setSelectedTable(tableName);
    try {
      const response = await fetch(`${API_URL}/admin/tables/${tableName}`, {
        headers: { token },
      });
      const data = await response.json();
      if (response.ok) {
        setTableRows(data.rows);
      }
    } catch {
      showAlert("Ошибка загрузки данных таблицы", true);
    }
  };

  const handleDeleteTableRecord = async (recordId: number | string) => {
    if (!selectedTable || loading) return;
    setLoading(true);
    try {
      const response = await fetch(
        `${API_URL}/admin/tables/${selectedTable}/${recordId}`,
        {
          method: "DELETE",
          headers: { token },
        }
      );
      const data = await response.json();
      if (!response.ok) {
        showAlert(data.detail || "Ошибка удаления записи", true);
        return;
      }
      showAlert("Запись удалена", false);
      fetchTableData(selectedTable);
    } catch {
      showAlert("Ошибка удаления записи", true);
    } finally {
      setLoading(false);
    }
  };

  const fetchAuditLogs = async () => {
    const params = new URLSearchParams();
    if (auditOpFilter) params.append("operation_type", auditOpFilter);
    try {
      const response = await fetch(
        `${API_URL}/admin/audit-logs?${params.toString()}`,
        { headers: { token } }
      );
      const data = await response.json();
      if (response.ok) {
        setAuditLogs(data.logs);
      }
    } catch {
      showAlert("Ошибка загрузки журнала аудита", true);
    }
  };

  const fetchSecretData = async () => {
    try {
      const response = await fetch(`${API_URL}/admin/secret-data`, {
        headers: { token },
      });
      const data = await response.json();
      if (response.ok) {
        setSecretData(data.items);
      }
    } catch {
      showAlert("Ошибка загрузки секретных данных", true);
    }
  };

  const fetchUsers = async () => {
    try {
      const response = await fetch(`${API_URL}/users`, {
        headers: { token },
      });
      const data = await response.json();
      if (response.ok) {
        setUsersList(data.users);
      }
    } catch {
      showAlert("Ошибка загрузки пользователей", true);
    }
  };

  const handleToggleStaffRole = async (
    targetLogin: string,
    currentRolesList: string[]
  ) => {
    if (loading) return;
    setLoading(true);

    const hasStaff = currentRolesList.includes("staff_group_role");
    const updatedRoles = hasStaff
      ? ["customer_group_role"]
      : ["customer_group_role", "staff_group_role"];

    try {
      const response = await fetch(`${API_URL}/roles`, {
        method: "POST",
        headers: { "Content-Type": "application/json", token },
        body: JSON.stringify({
          target_login: targetLogin,
          roles: updatedRoles,
        }),
      });
      const data = await response.json();
      if (response.ok) {
        showAlert(`Роли обновлены: ${targetLogin}`, false);
        fetchUsers();
      } else {
        showAlert(data.detail || "Ошибка смены роли", true);
      }
    } catch {
      showAlert("Ошибка обновления ролей", true);
    } finally {
      setLoading(false);
    }
  };

  const sortedAfisha = [...afisha].sort((a, b) => {
    if (afishaSort === "date_desc") {
      return (
        new Date(b.start_datetime).getTime() -
        new Date(a.start_datetime).getTime()
      );
    }
    if (afishaSort === "price_asc") {
      return Number(a.price_from || 0) - Number(b.price_from || 0);
    }
    if (afishaSort === "price_desc") {
      return Number(b.price_from || 0) - Number(a.price_from || 0);
    }
    return (
      new Date(a.start_datetime).getTime() -
      new Date(b.start_datetime).getTime()
    );
  });

  const sortedSales = [...salesList].sort((a, b) => {
    if (salesSort === "revenue_asc") {
      return Number(a.total_revenue) - Number(b.total_revenue);
    }
    if (salesSort === "occupancy_desc") {
      return b.occupancy_percent - a.occupancy_percent;
    }
    if (salesSort === "sold_desc") {
      return b.tickets_sold - a.tickets_sold;
    }
    return Number(b.total_revenue) - Number(a.total_revenue);
  });

  const sortedPopularity = [...popularityList].sort((a, b) => {
    if (popSort === "gross_asc") {
      return Number(a.total_gross) - Number(b.total_gross);
    }
    if (popSort === "tickets_desc") {
      return b.total_tickets_sold - a.total_tickets_sold;
    }
    if (popSort === "concerts_desc") {
      return b.total_concerts - a.total_concerts;
    }
    return Number(b.total_gross) - Number(a.total_gross);
  });

  const filteredTableRows = tableRows.filter((row) => {
    if (!tableSearch.trim()) return true;
    return Object.values(row).some((val) =>
      String(val ?? "")
        .toLowerCase()
        .includes(tableSearch.toLowerCase())
    );
  });

  if (!token) {
    return (
      <div className="container">
        <div className="auth-box">
          <div className="auth-title">ConcertHub</div>

          <div className="tabs">
            <button
              type="button"
              className={`tab-btn ${!isRegisterMode ? "active" : ""}`}
              onClick={() => {
                setIsRegisterMode(false);
                setAuthError("");
                setAuthSuccess("");
              }}
            >
              Вход
            </button>
            <button
              type="button"
              className={`tab-btn ${isRegisterMode ? "active" : ""}`}
              onClick={() => {
                setIsRegisterMode(true);
                setAuthError("");
                setAuthSuccess("");
              }}
            >
              Регистрация
            </button>
          </div>

          <div className="status-slot">
            {authError && (
              <div className="status-banner status-error">{authError}</div>
            )}
            {authSuccess && (
              <div className="status-banner status-success">{authSuccess}</div>
            )}
          </div>

          <form onSubmit={handleAuthSubmit}>
            <div className="form-group">
              <label>Логин</label>
              <input
                type="text"
                value={loginInput}
                onChange={(e) => setLoginInput(e.target.value)}
                required
                placeholder="Введите логин"
                disabled={loading}
              />
            </div>
            <div className="form-group">
              <label>Пароль</label>
              <input
                type="password"
                value={passwordInput}
                onChange={(e) => setPasswordInput(e.target.value)}
                required
                placeholder="••••••••"
                disabled={loading}
              />
            </div>
            <button type="submit" className="btn-submit" disabled={loading}>
              {loading
                ? "Загрузка..."
                : isRegisterMode
                ? "Зарегистрироваться"
                : "Войти"}
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="navbar">
        <div className="user-info">
          <span>Пользователь: </span>
          <strong>{currentLogin}</strong>
          {currentRoles.map((role) => (
            <span
              key={role}
              className={`badge ${
                role === "admin_group_role"
                  ? "badge-admin"
                  : role === "staff_group_role"
                  ? "badge-staff"
                  : ""
              }`}
            >
              {role}
            </span>
          ))}
        </div>
        <button onClick={handleLogout} className="btn-logout" disabled={loading}>
          Выйти
        </button>
      </div>

      <div className="tabs">
        <button
          type="button"
          className={`tab-btn ${activeTab === "afisha" ? "active" : ""}`}
          onClick={() => setActiveTab("afisha")}
        >
          Афиша концертов
        </button>
        <button
          type="button"
          className={`tab-btn ${activeTab === "tickets" ? "active" : ""}`}
          onClick={() => setActiveTab("tickets")}
        >
          Билеты пользователя
        </button>

        {isStaff && (
          <>
            <button
              type="button"
              className={`tab-btn ${activeTab === "sales" ? "active" : ""}`}
              onClick={() => setActiveTab("sales")}
            >
              Мониторинг продаж (GROUP BY)
            </button>
            <button
              type="button"
              className={`tab-btn ${activeTab === "venues" ? "active" : ""}`}
              onClick={() => setActiveTab("venues")}
            >
              Площадки и выпуск билетов
            </button>
            <button
              type="button"
              className={`tab-btn ${activeTab === "gate" ? "active" : ""}`}
              onClick={() => setActiveTab("gate")}
            >
              Контроль на входе
            </button>
          </>
        )}

        {isAdmin && (
          <>
            <button
              type="button"
              className={`tab-btn ${activeTab === "popularity" ? "active" : ""}`}
              onClick={() => setActiveTab("popularity")}
            >
              Популярность артистов (GROUP BY)
            </button>
            <button
              type="button"
              className={`tab-btn ${activeTab === "tables" ? "active" : ""}`}
              onClick={() => setActiveTab("tables")}
            >
              Все таблицы БД
            </button>
            <button
              type="button"
              className={`tab-btn ${activeTab === "audit" ? "active" : ""}`}
              onClick={() => setActiveTab("audit")}
            >
              Журнал аудита
            </button>
            <button
              type="button"
              className={`tab-btn ${activeTab === "secrets" ? "active" : ""}`}
              onClick={() => setActiveTab("secrets")}
            >
              Секретные данные
            </button>
            <button
              type="button"
              className={`tab-btn ${activeTab === "roles" ? "active" : ""}`}
              onClick={() => setActiveTab("roles")}
            >
              Управление ролями
            </button>
          </>
        )}
      </div>

      {actionAlert && (
        <div className="status-slot">
          <div
            className={`status-banner ${
              actionAlert.isError ? "status-error" : "status-success"
            }`}
          >
            {actionAlert.text}
          </div>
        </div>
      )}

      {activeTab === "afisha" && (
        <div className="panel">
          <div className="panel-header">
            <span className="panel-title">Афиша предстоящих концертов</span>
          </div>

          <div className="toolbar">
            <input
              type="text"
              placeholder="Фильтр по городу..."
              value={cityFilter}
              onChange={(e) => setCityFilter(e.target.value)}
            />
            <input
              type="text"
              placeholder="Фильтр по жанру..."
              value={genreFilter}
              onChange={(e) => setGenreFilter(e.target.value)}
            />
            <button type="button" onClick={fetchAfisha}>
              Применить фильтр
            </button>

            <select
              value={afishaSort}
              onChange={(e) => setAfishaSort(e.target.value)}
            >
              <option value="date_asc">Сортировка: по дате (сначала ближайшие)</option>
              <option value="date_desc">Сортировка: по дате (сначала поздние)</option>
              <option value="price_asc">Сортировка: по цене (по возрастанию)</option>
              <option value="price_desc">Сортировка: по цене (по убыванию)</option>
            </select>
          </div>

          <div className="afisha-grid">
            {sortedAfisha.map((item) => (
              <div key={item.concert_id} className="afisha-card">
                <div>
                  <div className="afisha-artist">{item.artist}</div>
                  <div className="afisha-program">{item.program_name}</div>
                </div>
                <div className="afisha-meta">
                  <div>Город: {item.city}</div>
                  <div>Площадка: {item.venue_name}</div>
                  <div>
                    Дата: {new Date(item.start_datetime).toLocaleString("ru-RU")}
                  </div>
                  <div>Возрастное ограничение: {item.age_restriction || "0+"}</div>
                  <div>
                    Свободно билетов: {item.available_tickets.length} шт.
                  </div>
                </div>
                <div className="afisha-price">
                  {item.price_from
                    ? `Билеты от ${item.price_from} руб.`
                    : "Нет доступных билетов"}
                </div>

                {item.available_tickets.length > 0 && (
                  <div className="form-group" style={{ marginBottom: "4px" }}>
                    <select
                      value={
                        selectedTickets[item.concert_id] ??
                        item.available_tickets[0].ticket_id
                      }
                      onChange={(e) =>
                        setSelectedTickets((prev) => ({
                          ...prev,
                          [item.concert_id]: Number(e.target.value),
                        }))
                      }
                    >
                      {item.available_tickets.map((opt) => (
                        <option key={opt.ticket_id} value={opt.ticket_id}>
                          {opt.sector_name} — {opt.price} руб. ({opt.barcode})
                        </option>
                      ))}
                    </select>
                  </div>
                )}

                <button
                  type="button"
                  className="btn-submit"
                  disabled={item.available_tickets.length === 0 || loading}
                  onClick={() => handleBuyConcertTicket(item)}
                >
                  {item.available_tickets.length > 0
                    ? "Купить выбранный билет"
                    : "Распродано"}
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === "tickets" && (
        <div className="panel">
          <div className="panel-header">
            <span className="panel-title">Купленные билеты</span>
          </div>

          <div className="data-table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Штрихкод</th>
                  <th>Исполнитель</th>
                  <th>Программа</th>
                  <th>Дата</th>
                  <th>Площадка</th>
                  <th>Сектор</th>
                  <th>Цена</th>
                  <th>Статус</th>
                  <th>Действие</th>
                </tr>
              </thead>
              <tbody>
                {userTickets.length === 0 ? (
                  <tr>
                    <td colSpan={10}>Нет купленных билетов</td>
                  </tr>
                ) : (
                  userTickets.map((t) => (
                    <tr key={t.ticket_id}>
                      <td>{t.ticket_id}</td>
                      <td>{t.barcode}</td>
                      <td>{t.artist}</td>
                      <td>{t.program_name}</td>
                      <td>{new Date(t.start_datetime).toLocaleString("ru-RU")}</td>
                      <td>{t.venue_name}</td>
                      <td>{t.sector_name}</td>
                      <td>{t.price} руб.</td>
                      <td>{t.ticket_status}</td>
                      <td>
                        <button
                          type="button"
                          className="btn-delete"
                          onClick={() => handleRefundTicket(t.ticket_id)}
                          disabled={loading}
                        >
                          Оформить возврат
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === "sales" && isStaff && (
        <div className="panel">
          <div className="panel-header">
            <span className="panel-title">
              Мониторинг продаж и заполняемости залов (GROUP BY)
            </span>
          </div>

          <div className="toolbar">
            <input
              type="text"
              placeholder="Фильтр по организатору..."
              value={promoterFilter}
              onChange={(e) => setPromoterFilter(e.target.value)}
            />
            <input
              type="text"
              placeholder="Фильтр по площадке..."
              value={venueFilter}
              onChange={(e) => setVenueFilter(e.target.value)}
            />
            <button type="button" onClick={fetchSalesMonitoring}>
              Фильтровать
            </button>

            <select
              value={salesSort}
              onChange={(e) => setSalesSort(e.target.value)}
            >
              <option value="revenue_desc">Сортировка: выручка (по убыванию)</option>
              <option value="revenue_asc">Сортировка: выручка (по возрастанию)</option>
              <option value="occupancy_desc">Сортировка: заполняемость (%)</option>
              <option value="sold_desc">Сортировка: продано билетов</option>
            </select>
          </div>

          <div className="data-table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Организатор</th>
                  <th>Исполнитель</th>
                  <th>Программа</th>
                  <th>Площадка</th>
                  <th>Вместимость</th>
                  <th>Продано билетов</th>
                  <th>Заполняемость (%)</th>
                  <th>Выручка</th>
                </tr>
              </thead>
              <tbody>
                {sortedSales.map((s, idx) => (
                  <tr key={idx}>
                    <td>{s.promoter}</td>
                    <td>{s.artist}</td>
                    <td>{s.program_name}</td>
                    <td>{s.venue_name}</td>
                    <td>{s.total_capacity}</td>
                    <td>{s.tickets_sold}</td>
                    <td>{s.occupancy_percent}%</td>
                    <td>{s.total_revenue} руб.</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === "venues" && isStaff && (
        <>
          <div className="two-col-grid">
            <div className="panel">
              <div className="panel-header">
                <span className="panel-title">Создать концерт</span>
              </div>
              <form onSubmit={handleCreateConcert}>
                <div className="form-group">
                  <label>Название программы</label>
                  <input
                    type="text"
                    value={programName}
                    onChange={(e) => setProgramName(e.target.value)}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Дата и время</label>
                  <input
                    type="datetime-local"
                    value={startDatetime}
                    onChange={(e) => setStartDatetime(e.target.value)}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Возрастное ограничение</label>
                  <input
                    type="text"
                    value={ageRestriction}
                    onChange={(e) => setAgeRestriction(e.target.value)}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>ID Артиста / ID Площадки / ID Организатора</label>
                  <div style={{ display: "flex", gap: "8px" }}>
                    <input
                      type="number"
                      value={artistId}
                      onChange={(e) => setArtistId(e.target.value)}
                      required
                    />
                    <input
                      type="number"
                      value={venueId}
                      onChange={(e) => setVenueId(e.target.value)}
                      required
                    />
                    <input
                      type="number"
                      value={promoterId}
                      onChange={(e) => setPromoterId(e.target.value)}
                      required
                    />
                  </div>
                </div>
                <button type="submit" className="btn-submit" disabled={loading}>
                  Добавить концерт
                </button>
              </form>
            </div>

            <div className="panel">
              <div className="panel-header">
                <span className="panel-title">Выпустить партию билетов в сектор</span>
              </div>
              <form onSubmit={handleReleaseTickets}>
                <div className="form-group">
                  <label>ID Концерта</label>
                  <input
                    type="number"
                    value={relConcertId}
                    onChange={(e) => setRelConcertId(e.target.value)}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>ID Сектора зала</label>
                  <input
                    type="number"
                    value={relSectorId}
                    onChange={(e) => setRelSectorId(e.target.value)}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Цена билета (руб.)</label>
                  <input
                    type="number"
                    value={relPrice}
                    onChange={(e) => setRelPrice(e.target.value)}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Количество билетов</label>
                  <input
                    type="number"
                    value={relCount}
                    onChange={(e) => setRelCount(e.target.value)}
                    required
                  />
                </div>
                <button type="submit" className="btn-submit" disabled={loading}>
                  Выпустить билеты
                </button>
              </form>
            </div>
          </div>

          <div className="panel">
            <div className="panel-header">
              <span className="panel-title">Конфигурация площадок и секторов</span>
            </div>
            <div className="data-table-wrapper">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>ID Площадки</th>
                    <th>Площадка</th>
                    <th>Город</th>
                    <th>Общая вместимость</th>
                    <th>ID Сектора</th>
                    <th>Сектор</th>
                    <th>Вместимость сектора</th>
                    <th>Тип сектора</th>
                  </tr>
                </thead>
                <tbody>
                  {venuesConfig.map((v) => (
                    <tr key={`${v.venue_id}-${v.sector_id}`}>
                      <td>{v.venue_id}</td>
                      <td>{v.venue_name}</td>
                      <td>{v.city}</td>
                      <td>{v.total_capacity}</td>
                      <td>{v.sector_id}</td>
                      <td>{v.sector_name}</td>
                      <td>{v.sector_capacity}</td>
                      <td>{v.sector_type}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}

      {activeTab === "gate" && isStaff && (
        <div className="panel">
          <div className="panel-header">
            <span className="panel-title">Контроль билетов на входе (Gate-Control)</span>
          </div>

          <form onSubmit={handleScanTicket} className="toolbar">
            <input
              type="text"
              placeholder="Введите штрихкод (напр. TK-990101)"
              value={scanBarcodeInput}
              onChange={(e) => setScanBarcodeInput(e.target.value)}
              required
            />
            <button type="submit" disabled={loading}>
              Проверить билет
            </button>
          </form>

          {scannedTicket && (
            <div className="data-table-wrapper">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>ID Концерта</th>
                    <th>Дата концерта</th>
                    <th>Штрихкод</th>
                    <th>Статус билета</th>
                    <th>Сектор</th>
                    <th>Тип сектора</th>
                    <th>Покупатель</th>
                    <th>Телефон</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>{scannedTicket.concert_id}</td>
                    <td>
                      {new Date(scannedTicket.start_datetime).toLocaleString("ru-RU")}
                    </td>
                    <td>{scannedTicket.barcode}</td>
                    <td>{scannedTicket.ticket_status}</td>
                    <td>{scannedTicket.sector_name}</td>
                    <td>{scannedTicket.sector_type}</td>
                    <td>{scannedTicket.customer_full_name || "Не указан"}</td>
                    <td>{scannedTicket.phone_number || "Не указан"}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {activeTab === "popularity" && isAdmin && (
        <div className="panel">
          <div className="panel-header">
            <span className="panel-title">
              Статистика популярности артистов (GROUP BY)
            </span>
          </div>

          <div className="toolbar">
            <input
              type="text"
              placeholder="Фильтр по жанру..."
              value={popGenreFilter}
              onChange={(e) => setPopGenreFilter(e.target.value)}
            />
            <button type="button" onClick={fetchArtistPopularity}>
              Фильтровать
            </button>

            <select value={popSort} onChange={(e) => setPopSort(e.target.value)}>
              <option value="gross_desc">Сортировка: общие сборы (по убыванию)</option>
              <option value="gross_asc">Сортировка: общие сборы (по возрастанию)</option>
              <option value="tickets_desc">Сортировка: продано билетов</option>
              <option value="concerts_desc">Сортировка: количество концертов</option>
            </select>
          </div>

          <div className="data-table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Исполнитель</th>
                  <th>Жанр</th>
                  <th>Всего концертов</th>
                  <th>Городов посещено</th>
                  <th>Продано билетов</th>
                  <th>Общая касса</th>
                </tr>
              </thead>
              <tbody>
                {sortedPopularity.map((p, idx) => (
                  <tr key={idx}>
                    <td>{p.artist}</td>
                    <td>{p.music_genre}</td>
                    <td>{p.total_concerts}</td>
                    <td>{p.cities_visited}</td>
                    <td>{p.total_tickets_sold}</td>
                    <td>{p.total_gross} руб.</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === "tables" && isAdmin && (
        <div className="panel">
          <div className="panel-header">
            <span className="panel-title">Просмотр всех таблиц базы данных</span>
          </div>

          <div className="table-chips">
            {tablesList.map((tbl) => (
              <button
                key={tbl}
                type="button"
                className={`chip-btn ${selectedTable === tbl ? "active" : ""}`}
                onClick={() => fetchTableData(tbl)}
              >
                {tbl}
              </button>
            ))}
          </div>

          <div className="toolbar">
            <input
              type="text"
              placeholder="Фильтр по строкам таблицы..."
              value={tableSearch}
              onChange={(e) => setTableSearch(e.target.value)}
            />
          </div>

          {filteredTableRows.length > 0 ? (
            <div className="data-table-wrapper">
              <table className="data-table">
                <thead>
                  <tr>
                    {Object.keys(filteredTableRows[0]).map((col) => (
                      <th key={col}>{col}</th>
                    ))}
                    <th>Удаление</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredTableRows.map((row, idx) => {
                    const pkKey = Object.keys(row)[0];
                    const pkVal = row[pkKey];
                    return (
                      <tr key={idx}>
                        {Object.keys(row).map((col) => (
                          <td key={col}>{String(row[col] ?? "")}</td>
                        ))}
                        <td>
                          {pkVal !== null && (
                            <button
                              type="button"
                              className="btn-delete"
                              onClick={() => handleDeleteTableRecord(pkVal)}
                              disabled={loading}
                            >
                              Удалить
                            </button>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          ) : (
            <div style={{ fontSize: "13px", color: "#888" }}>Нет записей</div>
          )}
        </div>
      )}

      {activeTab === "audit" && isAdmin && (
        <div className="panel">
          <div className="panel-header">
            <span className="panel-title">Журнал аудита (main_log)</span>
          </div>

          <div className="toolbar">
            <select
              value={auditOpFilter}
              onChange={(e) => setAuditOpFilter(e.target.value)}
            >
              <option value="">Все операции</option>
              <option value="I">INSERT (I)</option>
              <option value="U">UPDATE (U)</option>
              <option value="D">DELETE (D)</option>
            </select>
            <button type="button" onClick={fetchAuditLogs}>
              Обновить
            </button>
          </div>

          <div className="data-table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Тип операции</th>
                  <th>Дата и время</th>
                  <th>Оператор</th>
                  <th>Измененные данные</th>
                </tr>
              </thead>
              <tbody>
                {auditLogs.map((log) => (
                  <tr key={log.log_item_id}>
                    <td>{log.log_item_id}</td>
                    <td>{log.operation_type}</td>
                    <td>{log.operation_date}</td>
                    <td>{log.user_operator}</td>
                    <td>{log.changed_data}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === "secrets" && isAdmin && (
        <div className="panel">
          <div className="panel-header">
            <span className="panel-title">Зашифрованные данные (secret_data)</span>
          </div>

          <div className="data-table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Username (Encrypted)</th>
                  <th>Secret Token (Encrypted)</th>
                </tr>
              </thead>
              <tbody>
                {secretData.map((s) => (
                  <tr key={s.id}>
                    <td>{s.id}</td>
                    <td>{s.username}</td>
                    <td>{s.secret_token}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === "roles" && isAdmin && (
        <div className="panel">
          <div className="panel-header">
            <span className="panel-title">Управление ролями пользователей</span>
          </div>

          <div className="data-table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Логин</th>
                  <th>Текущие роли</th>
                  <th>Действие</th>
                </tr>
              </thead>
              <tbody>
                {usersList.map((u) => {
                  if (u.roles.includes("admin_group_role")) return null;
                  const hasStaff = u.roles.includes("staff_group_role");
                  return (
                    <tr key={u.login}>
                      <td>{u.login}</td>
                      <td>{u.roles.join(", ")}</td>
                      <td>
                        <button
                          type="button"
                          className="btn-role-action"
                          onClick={() => handleToggleStaffRole(u.login, u.roles)}
                          disabled={loading}
                        >
                          {hasStaff
                            ? "Снять роль staff_group_role"
                            : "Назначить staff_group_role"}
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}