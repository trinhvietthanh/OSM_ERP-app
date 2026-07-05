"use client";

import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { Plus, Trash2, UserPlus } from "lucide-react";

import { ApiError } from "@/lib/api";
import {
  createOrder,
  formatMoney,
  type CreateOrderInput,
} from "@/lib/orders";
import { createCustomer, listCustomers } from "@/lib/customers";
import { listProducts } from "@/lib/products";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { SearchSelect } from "@/components/ui/search-select";

type LineDraft = {
  product_id: string;
  qty: number;
  unit_price: string;
  unit_deposit: string;
};

const emptyLine = (): LineDraft => ({
  product_id: "",
  qty: 1,
  unit_price: "",
  unit_deposit: "",
});

/**
 * Create-order form, fully API-driven: customers + products come from the
 * backend; prices/deposits are free-form per line (hàng xách tay — no fixed
 * catalog price); optional "thu cọc ngay" records the first receipt in the
 * same request.
 */
export function CreateOrderForm({
  onCreated,
  onCancel,
}: {
  onCreated: () => void;
  onCancel: () => void;
}) {
  const queryClient = useQueryClient();

  const { data: customers = [] } = useQuery({
    queryKey: ["customers"],
    queryFn: () => listCustomers(),
  });
  const { data: products = [] } = useQuery({
    queryKey: ["products"],
    queryFn: listProducts,
  });

  const [customerId, setCustomerId] = useState("");
  const [lines, setLines] = useState<LineDraft[]>([emptyLine()]);
  const [separate, setSeparate] = useState(false);
  const [note, setNote] = useState("");
  const [deposit, setDeposit] = useState("");
  const [error, setError] = useState<string | null>(null);

  // Quick-create customer (inline mini form)
  const [showNewCustomer, setShowNewCustomer] = useState(false);
  const [newName, setNewName] = useState("");
  const [newPhone, setNewPhone] = useState("");

  const customerItems = useMemo(
    () =>
      customers.map((c) => ({
        value: c.id,
        label: c.name,
        meta: c.phone ?? undefined,
      })),
    [customers],
  );
  const productItems = useMemo(
    () =>
      products.map((p) => ({ value: p.id, label: p.name, meta: p.code })),
    [products],
  );

  const validLines = lines.filter(
    (line) => line.product_id && line.qty > 0 && Number(line.unit_price) > 0,
  );
  const totalQty = validLines.reduce((sum, line) => sum + line.qty, 0);
  const subtotal = validLines.reduce(
    (sum, line) => sum + Number(line.unit_price) * line.qty,
    0,
  );
  const depositDue = validLines.reduce(
    (sum, line) => sum + Number(line.unit_deposit || 0) * line.qty,
    0,
  );

  const customerMutation = useMutation({
    mutationFn: () =>
      createCustomer({ name: newName.trim(), phone: newPhone.trim() || undefined }),
    onSuccess: (customer) => {
      toast.success(`Đã thêm khách ${customer.name}`);
      queryClient.invalidateQueries({ queryKey: ["customers"] });
      setCustomerId(customer.id);
      setShowNewCustomer(false);
      setNewName("");
      setNewPhone("");
    },
    onError: (err: Error) =>
      toast.error(err instanceof ApiError ? err.message : "Có lỗi xảy ra"),
  });

  const orderMutation = useMutation({
    mutationFn: (input: CreateOrderInput) => createOrder(input),
    onSuccess: (order) => {
      toast.success(
        `Đã tạo đơn cho ${order.customer_name} — mã Code: ${order.tracking_code}`,
      );
      queryClient.invalidateQueries({ queryKey: ["orders"] });
      onCreated();
    },
    onError: (err: Error) =>
      toast.error(err instanceof ApiError ? err.message : "Có lỗi xảy ra"),
  });

  function updateLine(index: number, patch: Partial<LineDraft>) {
    setLines((prev) =>
      prev.map((line, i) => (i === index ? { ...line, ...patch } : line)),
    );
  }

  function submit() {
    if (!customerId) {
      setError("Vui lòng chọn khách hàng.");
      return;
    }
    if (validLines.length === 0) {
      setError("Thêm ít nhất một sản phẩm với số lượng và giá bán hợp lệ.");
      return;
    }
    setError(null);

    orderMutation.mutate({
      customer_id: customerId,
      lines: validLines.map((line) => ({
        product_id: line.product_id,
        quantity: line.qty,
        unit_price: line.unit_price,
        unit_deposit: line.unit_deposit || "0",
      })),
      is_separate: separate,
      note: note.trim(),
      initial_receipt:
        Number(deposit) > 0
          ? { amount: deposit, method: "bank_transfer", note: "Cọc khi tạo đơn" }
          : null,
    });
  }

  return (
    <div className="lg:grid lg:grid-cols-[minmax(0,1fr)_320px] lg:items-start lg:gap-6">
      {/* Form */}
      <div className="space-y-4">
        <Card>
          <CardHeader className="flex-row items-center justify-between">
            <CardTitle>Khách hàng</CardTitle>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              className="gap-1.5"
              onClick={() => setShowNewCustomer((v) => !v)}
            >
              <UserPlus aria-hidden />
              Thêm khách mới
            </Button>
          </CardHeader>
          <CardContent className="space-y-3">
            {showNewCustomer && (
              <div className="grid gap-2 rounded-lg border border-border p-3 sm:grid-cols-[minmax(0,1fr)_160px_auto]">
                <Input
                  value={newName}
                  onChange={(event) => setNewName(event.target.value)}
                  placeholder="Tên khách"
                  aria-label="Tên khách mới"
                />
                <Input
                  value={newPhone}
                  onChange={(event) => setNewPhone(event.target.value)}
                  placeholder="Số điện thoại"
                  aria-label="SĐT khách mới"
                  inputMode="tel"
                />
                <Button
                  type="button"
                  size="sm"
                  disabled={!newName.trim() || customerMutation.isPending}
                  onClick={() => customerMutation.mutate()}
                >
                  {customerMutation.isPending ? "Đang lưu…" : "Lưu khách"}
                </Button>
              </div>
            )}
            <div className="space-y-1.5">
              <Label htmlFor="customer">Khách hàng</Label>
              <SearchSelect
                items={customerItems}
                value={customerId}
                onChange={setCustomerId}
                placeholder="Tìm theo tên hoặc số điện thoại…"
                ariaLabel="Khách hàng"
                invalid={!customerId && !!error}
              />
            </div>
            <label className="flex cursor-pointer items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={separate}
                onChange={(event) => setSeparate(event.target.checked)}
                className="size-4 rounded border-input accent-primary"
              />
              <span className="text-muted-foreground">
                Giao riêng — không gom đơn
              </span>
            </label>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex-row items-center justify-between">
            <CardTitle>Sản phẩm</CardTitle>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              className="gap-1.5"
              onClick={() => setLines((prev) => [...prev, emptyLine()])}
            >
              <Plus aria-hidden />
              Thêm sản phẩm
            </Button>
          </CardHeader>
          <CardContent className="space-y-3">
            {lines.map((line, index) => (
              <div
                key={index}
                className="grid grid-cols-2 gap-2 rounded-lg border border-border p-2.5 sm:grid-cols-[minmax(0,1fr)_64px_110px_110px_32px] sm:items-center sm:border-0 sm:p-0"
              >
                <div className="col-span-2 sm:col-span-1">
                  <SearchSelect
                    items={productItems}
                    value={line.product_id}
                    onChange={(product_id) => updateLine(index, { product_id })}
                    placeholder="Chọn sản phẩm…"
                    ariaLabel="Sản phẩm"
                  />
                </div>
                <Input
                  type="number"
                  min={1}
                  value={line.qty}
                  onChange={(event) =>
                    updateLine(index, {
                      qty: Number.isFinite(event.target.valueAsNumber)
                        ? event.target.valueAsNumber
                        : 0,
                    })
                  }
                  aria-label="Số lượng"
                />
                <Input
                  type="number"
                  min={0}
                  step={1000}
                  value={line.unit_price}
                  onChange={(event) =>
                    updateLine(index, { unit_price: event.target.value })
                  }
                  placeholder="Giá bán"
                  aria-label="Giá bán"
                />
                <Input
                  type="number"
                  min={0}
                  step={1000}
                  value={line.unit_deposit}
                  onChange={(event) =>
                    updateLine(index, { unit_deposit: event.target.value })
                  }
                  placeholder="Cọc/món"
                  aria-label="Tiền cọc mỗi món"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="icon-sm"
                  aria-label="Xóa dòng"
                  className="justify-self-end sm:justify-self-auto"
                  onClick={() =>
                    setLines((prev) =>
                      prev.length > 1
                        ? prev.filter((_, i) => i !== index)
                        : [emptyLine()],
                    )
                  }
                >
                  <Trash2 aria-hidden />
                </Button>
              </div>
            ))}
            <div className="space-y-1.5 pt-1">
              <Label htmlFor="order-note">Ghi chú đơn</Label>
              <Input
                id="order-note"
                value={note}
                onChange={(event) => setNote(event.target.value)}
                placeholder="Ví dụ: khách cần trước 15/7…"
              />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Totals + actions */}
      <div className="mt-4 space-y-3 lg:sticky lg:top-20 lg:mt-0">
        <Card>
          <CardContent className="space-y-3 py-4">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Số dòng sản phẩm</span>
              <span className="font-medium tabular-nums">
                {validLines.length}
              </span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Tổng số lượng</span>
              <span className="font-medium tabular-nums">{totalQty}</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Cọc yêu cầu</span>
              <span className="font-medium tabular-nums">
                {formatMoney(depositDue)}
              </span>
            </div>
            <div className="border-t border-border pt-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Tổng tiền</span>
                <span className="text-xl font-semibold tabular-nums">
                  {formatMoney(subtotal)}
                </span>
              </div>
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="deposit-now">Thu cọc ngay (ghi phiếu thu)</Label>
              <Input
                id="deposit-now"
                type="number"
                min={0}
                step={1000}
                value={deposit}
                onChange={(event) => setDeposit(event.target.value)}
                placeholder={depositDue > 0 ? String(depositDue) : "0"}
              />
              {Number(deposit) > 0 && (
                <p className="text-xs text-muted-foreground">
                  Đơn sẽ chuyển sang <strong>Đã chốt</strong> sau khi thu cọc.
                </p>
              )}
            </div>
            {separate && (
              <p className="rounded-lg bg-muted px-2.5 py-1.5 text-xs text-muted-foreground">
                Đơn này sẽ được đánh dấu <strong>giao riêng</strong> và không đưa
                vào chuyến gom đơn.
              </p>
            )}
          </CardContent>
        </Card>

        {error && <p className="text-center text-xs text-destructive">{error}</p>}

        <div className="flex gap-2">
          <Button
            type="button"
            variant="outline"
            className="flex-1"
            onClick={onCancel}
            disabled={orderMutation.isPending}
          >
            Hủy
          </Button>
          <Button
            type="button"
            className="flex-[2]"
            onClick={submit}
            disabled={orderMutation.isPending}
          >
            {orderMutation.isPending ? "Đang lưu…" : "Lưu đơn"}
          </Button>
        </div>
      </div>
    </div>
  );
}
