defmodule CS2.Consumer.Retry do
  def retry?(code), do: code in ["timeout","unavailable","rate_limit"]
end
